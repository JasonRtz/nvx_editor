import sys
import os
from PyQt6.QtWidgets import QApplication
from src.app import App

def main():
    app = QApplication(sys.argv)

    app.setApplicationName("nvx_editor")

    window = App()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()