import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow, configure_dark_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)
    configure_dark_theme(app)  # Apply theme before creating window
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())