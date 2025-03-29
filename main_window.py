import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QTextEdit, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QMessageBox, QComboBox, QFileDialog, 
                             QAction, QMenuBar, QStatusBar, QProgressBar, QFrame, QSplitter, QGraphicsDropShadowEffect,
                             QToolBar, QSpacerItem, QSizePolicy, QDialog)
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import *
from display import DisplayWidget
from em_core import Emulator

def configure_dark_theme(app):
    """Centralized dark theme configuration"""
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 48))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

class StyledTextEdit(QTextEdit):
    """Custom styled text editor with line numbers and syntax highlighting"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2D2D30;
                color: #DCDCDC;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.setFont(QFont("Consolas", 10))
        self.highlighter = SyntaxHighlighter(self.document())

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlight_rules = []
        

        keywords = ["EP", "SET", "CLEAR", "WAIT", "LOOP", "STORE", 
                   "LOAD", "JUMP", "JUMPIF", "ADD", "SETALL", "SETNONE",
                   "SCRATCH_STORE", "SCRATCH_LOAD", "SCRATCH_ADD",
                   "SCRATCH_COPY", "SCRATCH_JUMPIF", "AND", "OR", 
                   "XOR", "NOT", "SUB", "SHL", "SHR"]
        
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF8C00"))
        self.highlight_rules.append((r'\b\d+\b', number_format))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#57A64A"))
        self.highlight_rules.append((r'#.*', comment_format))
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        for pattern in keywords:
            self.highlight_rules.append((fr'\b{pattern}\b', keyword_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlight_rules:
            regex = QRegularExpression(pattern)
            match_iterator = regex.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), 
                              match.capturedLength(), format)

class ControlButton(QPushButton):
    """Custom styled button for controls"""
    def __init__(self, text, icon_name=None, color="#007ACC", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(36)
        self.setCursor(Qt.PointingHandCursor)
        
        if icon_name:
            self.setIcon(QIcon(f"icons/{icon_name}.png"))
            self.setIconSize(QSize(16, 16))
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color, 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.9)};
            }}
        """)
    
    def lighten_color(self, color, factor=1.2):
        """Lighten a hex color by a factor"""
        col = QColor(color)
        h, s, l, a = col.getHslF()
        return QColor.fromHslF(h, s, min(1.0, l*factor), a).name()
        
    def darken_color(self, color, factor=0.8):
        """Darken a hex color by a factor"""
        col = QColor(color)
        h, s, l, a = col.getHslF()
        return QColor.fromHslF(h, s, max(0.0, l*factor), a).name()

class InfoPanel(QFrame):
    """Styled panel for information display"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 4px;
            }
            QLabel {
                color: #DCDCDC;
                font-weight: bold;
                padding: 4px;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border: 1px solid #3F3F46;
                border-radius: 2px;
                font-family: 'Consolas';
                font-size: 9pt;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        self.title_label = QLabel(title)
        layout.addWidget(self.title_label)
        
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setMaximumHeight(100)
        layout.addWidget(self.content)

class StatusLabel(QLabel):
    """Custom styled status label"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                color: #DCDCDC;
                padding: 2px 8px;
                background-color: #007ACC;
                border-radius: 10px;
                font-weight: bold;
            }
        """)

class ScratchpadPanel(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                padding: 8px;
            }
            QLabel {
                color: #DCDCDC;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(title))
        
        # Visual display grid
        self.bar_widget = QWidget()
        grid = QGridLayout(self.bar_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        
        self.bars = []
        for i in range(8):
            label = QLabel(f"S{i}")
            label.setAlignment(Qt.AlignCenter)
            
            bar = QProgressBar()
            bar.setRange(0, 255)
            bar.setTextVisible(False)
            bar.setStyleSheet("""
                QProgressBar {
                    background: #1E1E1E;
                    border: 1px solid #3F3F46;
                    border-radius: 2px;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background: #007ACC;
                }
            """)
            
            grid.addWidget(label, 0, i)
            grid.addWidget(bar, 1, i)
            self.bars.append(bar)
        
        layout.addWidget(self.bar_widget)

    def update_values(self, scratchpad):
        for i, value in enumerate(scratchpad):
            self.bars[i].setValue(value)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.setWindowIcon(QIcon("icon.png"))       

        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: #DCDCDC;
            }
            QMenuBar {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border-bottom: 1px solid #333333;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #3E3E40;
            }
            QMenu {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border: 1px solid #333333;
            }
            QMenu::item:selected {
                background-color: #3E3E40;
            }
            QStatusBar {
                background-color: #007ACC;
                color: white;
                font-weight: bold;
            }
            QLabel {
                color: #DCDCDC;
            }
            QComboBox {
                background-color: #3E3E40;
                color: #DCDCDC;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2D2D30;
                color: #DCDCDC;
                selection-background-color: #3F3F46;
            }
        """)
        
        self.initUI()
        # Initialize emulator with default RAM size 64
        self.emulator = Emulator(self.display, ram_size=64)
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_cycle)
        self.breakpoints = set()

    def initUI(self):
        self.setWindowTitle("Forgematrix")
        self.setGeometry(100, 100, 1200, 800)

        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()

        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.status_label = StatusLabel("Ready")
        self.statusBar.addWidget(self.status_label)

        # Create widgets
        self.display = DisplayWidget()
        # Apply shadow effect to display
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor("#3F3F3F"))
        shadow.setOffset(0, 0)
        self.display.setGraphicsEffect(shadow)
        
        # Make display have a nice border and background
        self.display.setStyleSheet("""
            background-color: #252526;
            border: 2px solid #3F3F46;
            border-radius: 8px;
            padding: 20px;
        """)
        
        # Editor with custom styling
        self.editor = StyledTextEdit()
        
        # Create modern buttons
        self.run_btn = ControlButton("Run", "play", "#28A745")
        self.stop_btn = ControlButton("Stop", "stop", "#DC3545")
        self.reset_btn = ControlButton("Reset", "reset", "#FFC107")
        self.help_btn = ControlButton("Help", "help", "#17A2B8")
        self.step_btn = ControlButton("Step", "step", "#6C757D")
        
        # Memory display panels
        self.memory_panel = InfoPanel("RAM (64 bytes)")
        self.memory_display = self.memory_panel.content
        
        self.scratchpad_panel = ScratchpadPanel("Scratchpad (8 bytes)")
        
        # Add program counter display
        self.pc_label = QLabel("PC: 0")
        self.pc_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                color: #DCDCDC;
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Error display
        self.error_display = QLabel("")
        self.error_display.setStyleSheet("""
            QLabel {
                color: #DC3545;
                background-color: #2A2A2C;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
        """)
        self.error_display.setWordWrap(True)

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        btn_layout.addWidget(self.help_btn)
        btn_layout.addWidget(self.step_btn)

        # Left side layout (display and controls)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.addWidget(QLabel("<h2>Display</h2>"))
        left_layout.addWidget(self.display, 1)
        left_layout.addLayout(btn_layout)
        left_layout.addWidget(self.pc_label)
        left_layout.addWidget(self.error_display)
        
        # Right side layout restructuring
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Program header
        program_header = QHBoxLayout()
        program_header.addWidget(QLabel("<h2>Program</h2>"))
        
        self.byte_counter = QLabel("0/64 BYTES USED")
        self.byte_counter.setStyleSheet("""
            QLabel {
                background-color: #252526;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                padding: 4px 8px;
            }
        """)
        program_header.addWidget(self.byte_counter)
        
        program_header.addWidget(QLabel("RAM Size:"))
        self.ram_combo = QComboBox()
        self.ram_combo.addItems(["32", "64", "128", "256"])
        self.ram_combo.setCurrentText("64")
        self.ram_combo.currentTextChanged.connect(self.on_ram_size_changed)
        program_header.addWidget(self.ram_combo)
        
        right_layout.addLayout(program_header)
        right_layout.addWidget(self.editor, 3)
        right_layout.addWidget(self.memory_panel, 1)
        right_layout.addWidget(self.scratchpad_panel, 1)

        # Create a splitter for resizable sections
        splitter = QSplitter(Qt.Horizontal)
        left_container = QWidget()
        left_container.setLayout(left_layout)
        right_container = QWidget()
        right_container.setLayout(right_layout)
        
        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setSizes([400, 800])  # Initial sizes
        
        # Set as central widget
        self.setCentralWidget(splitter)

        # Create horizontal splitter for editor + memory/scratchpad
        editor_memory_splitter = QSplitter(Qt.Horizontal)

        # Editor takes 70% width, memory/scratchpad 30%
        editor_memory_splitter.setSizes([700, 300])

        # Add editor to left side
        editor_memory_splitter.addWidget(self.editor)

        # Create vertical splitter for memory and scratchpad
        mem_scratch_splitter = QSplitter(Qt.Vertical)
        mem_scratch_splitter.addWidget(self.memory_panel)
        mem_scratch_splitter.addWidget(self.scratchpad_panel)
        mem_scratch_splitter.setSizes([200, 100])
        
        # Add vertical splitter to right side
        editor_memory_splitter.addWidget(mem_scratch_splitter)
        
        # Build right layout
        right_layout.addLayout(program_header)
        right_layout.addWidget(editor_memory_splitter)

        # Main splitter setup
        main_splitter = QSplitter(Qt.Horizontal)
        left_container = QWidget()
        left_container.setLayout(left_layout)
        right_container = QWidget()
        right_container.setLayout(right_layout)
        
        main_splitter.addWidget(left_container)
        main_splitter.addWidget(right_container)
        main_splitter.setSizes([500, 700])  # Initial proportions
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)  # Give editor area more space
        main_splitter.setHandleWidth(10)      # Make splitter more visible
        
        # Style splitters
        splitter_style = """
            QSplitter::handle {
                background: #3F3F46;
                width: 3px;
                height: 3px;
            }
            QSplitter::handle:hover {
                background: #007ACC;
            }
        """
        main_splitter.setStyleSheet(splitter_style)
        editor_memory_splitter.setStyleSheet(splitter_style)
        mem_scratch_splitter.setStyleSheet(splitter_style)

        self.setCentralWidget(main_splitter)
        self.setMinimumSize(1000, 600)

        # Connections
        self.run_btn.clicked.connect(self.start_emulation)
        self.stop_btn.clicked.connect(self.stop_emulation)
        self.reset_btn.clicked.connect(self.reset_emulation)
        self.help_btn.clicked.connect(self.show_help)
        self.editor.textChanged.connect(self.update_byte_counter)
        self.step_btn.clicked.connect(self.step_debug)

    def update_highlight(self):
        """Highlight the line corresponding to current PC"""
        self.editor.setExtraSelections([])  # Clear old highlights
        
        pc = self.emulator.pc
        line_num = self.emulator.pc_to_line.get(pc, None)
        
        if line_num is not None:
            doc = self.editor.document()
            block = doc.findBlockByLineNumber(line_num - 1)  # Convert to 0-based index
            
            if block.isValid():
                # Create highlight
                cursor = QTextCursor(block)
                selection = QTextEdit.ExtraSelection()
                selection.format.setBackground(QColor("#264F78"))
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                
                # Apply highlight
                self.editor.setExtraSelections([selection])
                self.editor.setTextCursor(cursor)
                self.editor.ensureCursorVisible()

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #252526;
                border-bottom: 1px solid #3F3F46;
                spacing: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #3E3E40;
            }
            QToolButton:pressed {
                background-color: #007ACC;
            }
        """)
        
        # Toolbar actions
        new_action = QAction(QIcon("icons/new.png"), "New", self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction(QIcon("icons/open.png"), "Open", self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction(QIcon("icons/save.png"), "Save", self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        self.addToolBar(toolbar)

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        saveas_action = QAction('Save As...', self)
        saveas_action.setShortcut('Ctrl+Shift+S')
        saveas_action.triggered.connect(self.save_as_file)
        file_menu.addAction(saveas_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        QMessageBox.about(self, "About Forgematrix",
                        "Forgematrix Emulator\nVersion 1.0\nDeveloped by\n"
                        "Draconiator: Initial vision, Architect, Implementor\n"
                        "Claude: Initial Implementation\n"
                        "Deepseek-R3: Coding, Debugging\n"
                        "Google Gemini: Additional Support\n\n"
                        "A simple but powerful emulator for a custom 2-bit processor architecture.\n"
                        "(C) 2025 Draconiator")


    def update_byte_counter(self):
        """Update the byte counter based on program code."""
        code = self.editor.toPlainText().split('\n')
        ram_ptr = 0
        valid = True
        invalid_chars = False

        try:
            for line in code:
                line = line.strip().upper()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                if not parts:
                    continue

                cmd = parts[0]
                try:
                    if cmd == "EP":
                        continue

                    # Handle SET/CLEAR with multiple pairs
                    elif cmd in {"SET", "CLEAR"}:
                        params_str = ' '.join(parts[1:])
                        pairs = []
                        for pair in params_str.split(','):
                            pair = pair.strip()
                            if not pair:
                                continue
                            try:
                                x, y = pair.split()
                                pairs.append((x, y))
                            except:
                                invalid_chars = True
                        if pairs:
                            ram_ptr += 1 + 1 + 2 * len(pairs)  # 1 byte opcode + 1 byte count + 2 bytes per pair
                        else:
                            invalid_chars = True

                    # Existing logic for other commands
                    elif cmd in {"STORE", "JUMPIF", "SCRATCH_STORE", 
                                "SCRATCH_LOAD", "SCRATCH_COPY", "SCRATCH_JUMPIF", 
                                "NOT", "SHL", "SHR"}:
                        ram_ptr += 3
                    elif cmd in {"WAIT", "LOAD", "JUMP"}:
                        ram_ptr += 2
                    elif cmd in {"LOOP", "SETALL", "SETNONE"}:
                        ram_ptr += 1
                    elif cmd in {"ADD", "SCRATCH_ADD", "AND", "OR", "XOR", "SUB"}:
                        ram_ptr += 4
                    else:
                        invalid_chars = True

                except Exception as e:
                    invalid_chars = True

            status_text = f"{ram_ptr}/{self.emulator.ram_size} BYTES USED"

            if invalid_chars:
                status_text += " - INVALID SYNTAX"
                valid = False
            elif ram_ptr > self.emulator.ram_size:
                status_text += " - OVER CAPACITY!"
                valid = False
            elif ram_ptr > self.emulator.ram_size * 0.8:
                valid = False  # Warning state (yellow)

            self.byte_counter.setText(status_text)
            self.byte_counter.setProperty("valid", valid)
            self.byte_counter.style().unpolish(self.byte_counter)
            self.byte_counter.style().polish(self.byte_counter)

        except Exception as e:
            self.byte_counter.setText("SYNTAX ERROR IN PROGRAM")
            self.byte_counter.setProperty("valid", False)
            self.byte_counter.style().unpolish(self.byte_counter)
            self.byte_counter.style().polish(self.byte_counter)

    def start_emulation(self):
        code = self.editor.toPlainText().split('\n')
        
        # Reset emulator and load the program into RAM
        success = self.emulator.parse_and_load_program(code)
        
        if not success:
            self.error_display.setText(self.emulator.error)
            self.status_label.setText("Error loading program")
            return
            
        self.error_display.setText("")
        self.emulator.running = True
        self.timer.start(8)  # Run at ~120Hz
        self.status_label.setText("Running...")
        self.update_memory_display()
        self.update_pc_display()

    def stop_emulation(self):
        self.timer.stop()
        self.emulator.running = False
        self.status_label.setText("Stopped")
        
        if self.emulator.error:
            self.error_display.setText(self.emulator.error)

    def reset_emulation(self):
        self.stop_emulation()
        self.emulator.reset()
        self.error_display.setText("")
        self.update_memory_display()
        self.update_pc_display()
        self.status_label.setText("Reset completed")
        self.editor.setExtraSelections([])
        self.editor.repaint()

    def on_ram_size_changed(self, size_str):
        """Handle RAM size change event"""
        new_size = int(size_str)
        self.emulator = Emulator(self.display, ram_size=new_size)
        self.reset_emulation()
        self.memory_panel.title_label.setText(f"RAM ({new_size} bytes)")
        self.update_byte_counter()
        # Prevent layout resizing
        self.memory_panel.setMinimumWidth(250)
        self.memory_panel.setMaximumWidth(350)

    def toggle_breakpoint(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        if line in self.breakpoints:
            self.breakpoints.remove(line)
        else:
            self.breakpoints.add(line)
        self.highlight_current_line()

    def highlight_current_line(self):
        extra_selections = []
        cursor = QTextEdit.ExtraSelection()
        line_color = QColor("#264F78")
        cursor.format.setBackground(line_color)
        cursor.format.setProperty(QTextFormat.FullWidthSelection, True)
        cursor.cursor = self.editor.textCursor()
        cursor.cursor.clearSelection()
        extra_selections.append(cursor)
        self.editor.setExtraSelections(extra_selections)

    def step_debug(self):
        if not self.emulator.running:
            code = self.editor.toPlainText().split('\n')
            if not self.emulator.parse_and_load_program(code):
                return
            self.emulator.running = True

        self.emulator.step()
        self.update_pc_display()
        self.update_highlight()
        self.update_memory_display()

        if self.emulator.pc in self.breakpoints:
            self.stop_emulation()

    def run_cycle(self):
        if self.emulator.running:
            self.emulator.step()
            
            # Update PC display each cycle
            self.update_pc_display()
            self.update_highlight()
            
            # Update memory display every 30 cycles
            if self.emulator.pc % 30 == 0:
                self.update_memory_display()
                
            # Check for errors
            if self.emulator.error:
                self.error_display.setText(self.emulator.error)
                self.stop_emulation()

    def update_memory_display(self):
        mem_text = ""
        for i in range(0, self.emulator.ram_size, 8):
            row = f"{i:02d}: "
            row += " ".join(f"{self.emulator.ram[i+j]:02X}" for j in range(8))
            mem_text += row + "\n"
        self.memory_display.setText(mem_text)
        self.scratchpad_panel.update_values(self.emulator.scratchpad)
        
    def update_pc_display(self):
        pc_text = f"PC: {self.emulator.pc}"
    
        # Show WAIT cycles if active
        if self.emulator.delay > 0:
            pc_text += f" | WAIT: {self.emulator.active_delay - self.emulator.delay + 1}/{self.emulator.active_delay}"
    
        self.pc_label.setText(pc_text)

        """Update the byte counter based on program code."""
        code = self.editor.toPlainText().split('\n')
        ram_ptr = 0
        valid = True
        invalid_chars = False

        try:
            for line in code:
                line = line.strip().upper()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                if not parts:
                    continue

                cmd = parts[0]
                try:
                    if cmd == "EP":
                        continue

                    # Handle SET/CLEAR with multiple pairs
                    elif cmd in {"SET", "CLEAR"}:
                        params_str = ' '.join(parts[1:])
                        pairs = []
                        for pair in params_str.split(','):
                            pair = pair.strip()
                            if not pair:
                                continue
                            try:
                                x, y = pair.split()
                                pairs.append((x, y))
                            except:
                                invalid_chars = True
                        if pairs:
                            ram_ptr += 1 + 1 + 2 * len(pairs)  # 1 byte opcode + 1 byte count + 2 bytes per pair
                        else:
                            invalid_chars = True

                    # Existing logic for other commands
                    elif cmd in {"STORE", "JUMPIF", "SCRATCH_STORE", 
                                "SCRATCH_LOAD", "SCRATCH_COPY", "SCRATCH_JUMPIF", 
                                "NOT", "SHL", "SHR"}:
                        ram_ptr += 3
                    elif cmd in {"WAIT", "LOAD", "JUMP"}:
                        ram_ptr += 2
                    elif cmd in {"LOOP", "SETALL", "SETNONE"}:
                        ram_ptr += 1
                    elif cmd in {"ADD", "SCRATCH_ADD", "AND", "OR", "XOR", "SUB"}:
                        ram_ptr += 4
                    else:
                        invalid_chars = True

                except Exception as e:
                    invalid_chars = True

            status_text = f"{ram_ptr}/{self.emulator.ram_size} BYTES USED"

            if invalid_chars:
                status_text += " - INVALID SYNTAX"
                valid = False
            elif ram_ptr > self.emulator.ram_size:
                status_text += " - OVER CAPACITY!"
                valid = False
            elif ram_ptr > self.emulator.ram_size * 0.8:
                valid = False  # Warning state (yellow)

            self.byte_counter.setText(status_text)
            self.byte_counter.setProperty("valid", valid)
            self.byte_counter.style().unpolish(self.byte_counter)
            self.byte_counter.style().polish(self.byte_counter)

        except Exception as e:
            self.byte_counter.setText("SYNTAX ERROR IN PROGRAM")
            self.byte_counter.setProperty("valid", False)
            self.byte_counter.style().unpolish(self.byte_counter)
            self.byte_counter.style().polish(self.byte_counter)

    def new_file(self):
        if self.check_save_needed():
            self.editor.clear()
            self.current_file = None
            self.setWindowTitle("2-bit Processor - Untitled")
            self.status_label.setText("New file created")

    def open_file(self):
        if self.check_save_needed():
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open Program", "", "2-bit Files (*.2b);;Text Files (*.txt);;All Files (*)", 
                options=options
            )
            if file_name:
                self.load_file(file_name)

    def save_file(self):
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Program", "", "2-bit Files (*.2b);;Text Files (*.txt);;All Files (*)", 
            options=options
        )
        if file_name:
            # Add .2b extension if no extension provided
            if not any(file_name.endswith(ext) for ext in ['.2b', '.txt']):
                file_name += '.2b'
            self._save_to_file(file_name)

    def load_file(self, filename):
        try:
            with open(filename, 'r') as f:
                content = f.read()
                self.editor.setText(content)
                self.current_file = filename
                self.setWindowTitle(f"2-bit Processor - {os.path.basename(filename)}")
                self.status_label.setText(f"Loaded {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading file: {e}")

    def _save_to_file(self, filename):
        try:
            content = self.editor.toPlainText()
            with open(filename, 'w') as f:
                f.write(content)
                
            self.current_file = filename
            self.setWindowTitle(f"2-bit Processor - {os.path.basename(filename)}")
            self.status_label.setText(f"Saved to {filename}")
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving file: {e}")
            return False

    def check_save_needed(self):
        if self.editor.document().isModified() and self.editor.toPlainText():
            reply = QMessageBox.question(
                self, 'Save Changes', 
                'Do you want to save your changes?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                return self.save_file()
            elif reply == QMessageBox.Cancel:
                return False
        
        return True

    def show_help(self):
        help_text = """<h2>Forgematrix Programming Guide</h2>
        <p>A simple emulator for a 2-bit processor with:</p>
        <ul>
            <li>4x4 pixel display</li>
            <li>64 bytes of RAM for both code and data</li>
            <li>Running at 120Hz</li>
        </ul>
        <p>The perfect platform for minimal computing!</p>
        <h3>Basic Commands:</h3>
        <p><code>EP x</code> - Start the program at byte (x)<br>
        <code>SET x y</code> - Lights up pixel at position (x,y)<br>
        <code>CLEAR x y</code> - Turns off pixel at position (x,y)<br>
        Alternatively, you can separate these with commas, E.G. SET 0 0,0 1,0 2
        <code>WAIT n</code> - Pauses execution for n cycles<br>
        <code>LOOP</code> - Jumps back to first instruction<br>
        <code>SETALL</code> - Turns on all pixels<br>
        <code>SETNONE</code> - Turns off all pixels</p>
        <h3>Memory Commands:</h3>
        <p><code>STORE a v</code> - Store value v in RAM at address a<br>
        <code>LOAD a</code> - Load value from RAM address a (demonstrates by setting pixel 0,0)<br>
        <code>JUMP a</code> - Jump to instruction at position a<br>
        <code>JUMPIF a r</code> - Jump to instruction a if RAM address r is non-zero<br>
        <code>ADD a b c</code> - Add value at RAM address a to value at b, store result in c</p>
        <h3>Scratchpad Commands:</h3>
        <p><code>SCRATCH_STORE s v</code> - Store value v in scratchpad address s (0-7)<br>
        <code>SCRATCH_LOAD s a</code> - Load value from scratchpad s to RAM address a<br>
        <code>SCRATCH_ADD s1 s2 d</code> - Add scratchpad s1 and s2, store result in scratchpad d<br>
        <code>SCRATCH_COPY a s</code> - Copy RAM address a to scratchpad s<br>
        <code>SCRATCH_JUMPIF a s</code> - Jump to address a if scratchpad s is non-zero</p>
        <h3>Bitwise Commands:</h3>
        <p><code>AND a b c</code> - Bitwise AND of RAM[a] and RAM[b], store in RAM[c]<br>
        <code>OR a b c</code> - Bitwise OR of RAM[a] and RAM[b], store in RAM[c]<br>
        <code>XOR a b c</code> - Bitwise XOR of RAM[a] and RAM[b], store in RAM[c]<br>
        <code>NOT a b</code> - Bitwise NOT of RAM[a], store in RAM[b]<br>
        <code>SHL a b</code> - Shift RAM[a] left by 1 bit, store in RAM[b]<br>
        <code>SHR a b</code> - Shift RAM[a] right by 1 bit, store in RAM[b]</p>
        <h3>Math Commands:</h3>
        <p><code>SUB a b c</code> - Subtract RAM[b] from RAM[a], store in RAM[c]</p>
        <h3>RAM Usage:</h3>
        <ul>
            <li>Each instruction requires space in RAM:<br>
                <code>ADD/SCRATCH_ADD/AND/OR/XOR/SUB</code>: 4 bytes<br>
                <code>SET/CLEAR/STORE/JUMPIF/SCRATCH_STORE/SCRATCH_LOAD/SCRATCH_COPY/SCRATCH_JUMPIF/NOT/SHL/SHR</code>: 3 bytes<br>
                <code>WAIT/LOAD/JUMP</code>: 2 bytes<br>
                <code>LOOP/SETALL/SETNONE</code>: 1 byte</li>
            <li>Program code and data share the same RAM</li>
            <li>Scratchpad: 8 persistent bytes (saved between runs)</li>
            <li>Execution stops when all RAM is used or an error occurs</li>
        </ul>
        """
        # Create a QDialog instead of QMessageBox
        self.help_dialog = QDialog(self)
        self.help_dialog.setWindowTitle("Help")
        self.help_dialog.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
    
        # Set up layout and content
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(help_text)
        text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(text_edit)
    
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.help_dialog.close)
        layout.addWidget(close_btn)
    
        # Styling
        self.help_dialog.setStyleSheet("""
            QDialog {
                background-color: #252526;
                color: #FFFFFF;
            }
            QTextEdit {
                background-color: #1E1E1E;
                border: 1px solid #3F3F46;
                padding: 12px;
                font-family: 'Consolas';
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
    
        self.help_dialog.setLayout(layout)
        self.help_dialog.resize(800, 600)
        self.help_dialog.show()

    def closeEvent(self, event):
        # Handle window close event with save check
        if self.check_save_needed():
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    configure_dark_theme(app)  # Use centralized config
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())