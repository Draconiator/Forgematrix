from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt

class DisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.grid_size = 4
        self.pixels = []
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        layout.setSpacing(0)
        for y in range(self.grid_size):
            row = []
            for x in range(self.grid_size):
                pixel = QLabel()
                pixel.setFixedSize(200, 200)
                pixel.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align text to top-left
                pixel.setText(f"{x} {y}")  # Set coordinate text
                # Initial styling (black background, white text)
                pixel.setStyleSheet("""
                    background-color: black;
                    color: white;
                    font-size: 12px;
                    padding: 4px;
                """)
                layout.addWidget(pixel, y, x)
                row.append(pixel)
            self.pixels.append(row)
        self.setLayout(layout)

    def update_pixel(self, x, y, state):
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return  # Ignore invalid coordinates
        # Set background and text color based on state
        bg_color = "white" if state else "black"
        text_color = "black" if state else "white"
        self.pixels[y][x].setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            font-size: 12px;
            padding: 4px;
        """)
        
    def clear_all(self):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                self.pixels[y][x].setStyleSheet("""
                    background-color: black;
                    color: white;
                    font-size: 12px;
                    padding: 4px;
                """)