from src.app import App
from PyQt6.QtWidgets import QApplication
import sys
import os

def main():
    os.environ["QT_AUTOSCREENSCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()