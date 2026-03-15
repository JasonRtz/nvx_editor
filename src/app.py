import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QTextEdit, QFileDialog, QMessageBox)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NVX Editor")
        self.resize(800, 600)
        

        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        self.current_file = None

        icon_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "nvx_editor.png"))

        try:
            icon = QIcon(icon_path)
            if icon.isNull():
                raise ValueError(f"Failed to load icon data: {icon_path}")

            self.setWindowIcon(icon)

        except Exception as e:
            print(f"[WARN] Could not set window icon ({icon_path}): {e}")

        self.view()

    def view(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        
        #File actions
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.file_open)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.file_save)

        save_as_action = QAction("Save &As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.file_save_as)

        print_action = QAction("&Print", self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_file)

        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(print_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        edit_menu = menu_bar.addMenu("&Edit")

        cut_action = QAction("&Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.editor.cut)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.editor.copy) 

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.editor.paste)

        select_all_action = QAction("&Select All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.editor.selectAll)

        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addAction(select_all_action)

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
        about_action.triggered.connect(self.about_dialog)
        help_menu.addAction(about_action)
    
    def about_dialog(self, event):
        QMessageBox.about(self, "About NVX Editor",
                            "NVX Text Editor\n"
                            "Built with Python and Qt\n"
                            "Version 0.1"
        )

    def closeEvent(self, event):
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self, 'Save Changes?',
                "You have unsaved changes. Do you want to save them before exiting?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                self.file_save()
                event.accept() 
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept() 
            else:
                event.ignore()
        else:
            event.accept() 

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", 
                                             "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.editor.setPlainText(text)
                self.current_file = path
                self.setWindowTitle(f"NVX Editor - {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def file_save(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(self, "Save File", "", 
                                                 "Text File (*.txt);;All Files (*)")
            if not path:
                return
            self.current_file = path
            
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            
            self.editor.document().setModified(False)
            
            self.setWindowTitle(f"NVX Editor - {self.current_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")
    
    def file_save_as(self):
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "Text File (*.txt);;PDF File (*.pdf);;All Files (*)"
        )

        if not path:
            return

        try:
            if path.endswith(".pdf"):
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(path)

                self.editor.document().print(printer)

            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())

            self.current_file = path
            self.editor.document().setModified(False)
            self.setWindowTitle(f"NVX Editor - {path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def print_file(self):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    
        dialog = QPrintDialog(printer, self)
    
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.editor.print_(printer)