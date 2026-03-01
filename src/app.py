import sys
from PyQt6.QtWidgets import (QMainWindow, QTextEdit, QFileDialog, QMessageBox)
from PyQt6.QtGui import QAction, QIcon


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NVX Editor")
        self.resize(800, 600)

        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)

        self.view()

    def view(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        view_menu = menu_bar.addMenu("&View")
        help_menu = menu_bar.addMenu("&Help")