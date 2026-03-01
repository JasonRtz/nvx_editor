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
        
        #File actions
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")

        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("&View")

        #View actions

        zoom_in_action = QAction("&Zoom In", self)
        zoom_in_action.setShortcut("Ctrl+=") 
        zoom_in_action.triggered.connect(self.editor.zoomIn) 
        
        zoom_out_action = QAction("&Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.editor.zoomOut) 
        
        view_menu.addAction(zoom_in_action)
        view_menu.addAction(zoom_out_action)

        help_menu = menu_bar.addMenu("&Help")
        
        #Help actions

        about_action = QAction("&About", self)

        help_menu.addAction(about_action)