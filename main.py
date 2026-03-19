import sys
import os
from PyQt6.QtWidgets import QApplication
from src.app import App

def main():
    os.environ["QT_AUTOSCREENSCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)

    app.setOrganizationName("NVX")
    app.setApplicationName("NVXEditor")

    window = App()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()