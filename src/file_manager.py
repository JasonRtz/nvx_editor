from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter

class File_Manager:
    def __init__(self, app_instance):
        # Initialize file manager with reference to main App instance.
        self.app = app_instance  
    
    def new_file(self):
        # Create a new file buffer, prompting to save changes first if needed.
        if self.app.editor.document().isModified():
            reply = QMessageBox.question(
                self.app, 'Save Changes?',
                "Save current file before creating a new one?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.file_save()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.app.editor.clear()
        self.app.current_file = None
        self.app.setWindowTitle("NVX Editor")

    def file_open(self):
        # Show open file dialog and load selected file into editor.
        path, _ = QFileDialog.getOpenFileName(self.app, "Open File", "", 
                                             "Text File (*.txt);;All Files (*)")
        if path:
            self.open_recent_file(path)
    
    def open_recent_file(self, path):
        # Load file content from path into editor and update recent list.
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.app.editor.setPlainText(text)
            self.app.current_file = path
            self.app.setWindowTitle(f"NVX Editor - {path}")
            self.update_recent_files(path)
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Could not open file: {e}")
    
    def file_save(self):
        # Save current contents to current file path; delegate to Save As when no file selected.
        if not self.app.current_file:
            self.file_save_as()
            return
            
        try:
            with open(self.app.current_file, 'w', encoding='utf-8') as f:
                f.write(self.app.editor.toPlainText())

            self.app.editor.document().setModified(False)
            self.app.setWindowTitle(f"NVX Editor - {self.app.current_file}")
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Could not save file: {e}")
    
    def file_save_as(self):
        # Show Save As dialog and write content to chosen path (includes PDF support).
        path, _ = QFileDialog.getSaveFileName(self.app, "Save File As", "",
                                             "Text File (*.txt);;PDF File (*.pdf);;All Files (*)")
        if not path:
            return

        try:
            if path.endswith(".pdf"):
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(path)
                self.app.editor.document().print(printer)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.app.editor.toPlainText())

            self.app.current_file = path
            self.update_recent_files(path)
            self.app.editor.document().setModified(False)
            self.app.setWindowTitle(f"NVX Editor - {path}")
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Could not save file: {e}")
    
    def update_recent_files(self, path):
        # Add a path to recently opened files, keep list trimmed, and persist settings.
        if not path:
            return
        
        if path in self.app.recent_files:
            self.app.recent_files.remove(path)
        
        self.app.recent_files.insert(0, path)
        self.app.recent_files = self.app.recent_files[:10]
        
        self.app.update_recent_actions()
        
        current_font = self.app.editor.font().family()
        current_size = self.app.editor.font().pointSize()
        tab_val = int(self.app.editor.tabStopDistance() / self.app.editor.fontMetrics().horizontalAdvance(' '))
        self.app.save_settings_to_json(current_font, current_size, self.app.current_theme, tab_val)

    def clear_recent_files(self):
        # Clear recent files list in UI and save settings.
        self.app.recent_files = []
        self.app.update_recent_actions()
        
        current_font = self.app.editor.font().family()
        current_size = self.app.editor.font().pointSize()
        tab_val = int(self.app.editor.tabStopDistance() / self.app.editor.fontMetrics().horizontalAdvance(' '))
        self.app.save_settings_to_json(current_font, current_size, self.app.current_theme, tab_val)

    def print_file(self):
        # Open print dialog and print the current document if confirmed.
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self.app)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.app.editor.print(printer)

    def handle_close_event(self, event):
        # Prompt to save unsaved changes when window is closing.
        # Centralized close logic.
        if self.app.editor.document().isModified():
            reply = QMessageBox.question(
                self.app, 'Save Changes?',
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