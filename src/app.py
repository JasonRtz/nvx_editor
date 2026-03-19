import os
import sys
import json
from pathlib import Path
from PyQt6.QtCore import QStandardPaths
from PyQt6.QtWidgets import (QApplication, QDialog, QInputDialog, QMainWindow, QTextEdit, QFileDialog, QMessageBox, QLabel)
from PyQt6.QtGui import QAction, QColor, QIcon, QKeySequence, QFont, QTextCursor, QTextFormat
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from .settings import Settings

# NVX Editor application main window class.
# Manages file operations, edit actions, view actions, print, and settings persistence.
class App(QMainWindow):
    def resource_base_path(self):
        # Determine the path to bundled assets for both dev and frozen exe.
        # When packaged with PyInstaller, Qt app resources are extracted to
        # a temporary folder and sys._MEIPASS is set. This returns that path.
        # Otherwise, returns the directory of this source file.
        if getattr(sys, '_MEIPASS', None):
            return Path(sys._MEIPASS)
        return Path(__file__).resolve().parent

    def __init__(self):
        # Window setup
        super().__init__()
        self.setWindowTitle("NVX Editor")
        self.resize(800, 600)
        self.current_theme = "Light"

        # Editor widget as central widget
        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        self.current_file = None

        # Load saved settings (font + theme) from disk (if present)
        self.load_settings_from_json()

        # Application icon (.exe bundling via PyInstaller may set _MEIPASS)
        icon_path = os.path.normpath(str(self.resource_base_path() / "data" / "icons" / "nvx_editor.png"))

        try:
            icon = QIcon(icon_path)
            if icon.isNull():
                raise ValueError(f"Failed to load icon data: {icon_path}")

            self.setWindowIcon(icon)

        except Exception as e:
            print(f"Could not set window icon ({icon_path}): {e}")

        # Build UI menus and actions
        self.view()

        self.status_bar = self.statusBar()
        self.status_label = QLabel("Line: 1, Col: 1 | Characters: 0")
        self.status_bar.addPermanentWidget(self.status_label)

        self.editor.cursorPositionChanged.connect(self.update_status_bar)

    def view(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        
        #File actions

        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        

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

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(print_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        edit_menu = menu_bar.addMenu("&Edit")

        undo_action = QAction("&Undo",self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.editor.undo)

        redo_action = QAction("&Redo",self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.editor.redo)

        cut_action = QAction("&Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.editor.cut)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.editor.copy) 

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.editor.paste)

        delete_action = QAction("&Delete",self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.handle_delete)

        find_action = QAction("&Find",self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find_text)

        select_all_action = QAction("&Select All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.editor.selectAll)

        settings_action = QAction("&Settings",self)
        settings_action.triggered.connect(self.show_settings)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addAction(delete_action)
        edit_menu.addAction(find_action)
        edit_menu.addAction(select_all_action)
        edit_menu.addSeparator()
        edit_menu.addAction(settings_action)

        view_menu = menu_bar.addMenu("&View")

        #View actions

        zoom_in_action = QAction("&Zoom In", self)
        zoom_in_action.setShortcut("Ctrl+=") 
        zoom_in_action.triggered.connect(self.editor.zoomIn) 
        
        zoom_out_action = QAction("&Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.editor.zoomOut) 
        
        full_screen_action = QAction("&Full Screen", self)
        full_screen_action.setShortcut("F11")
        full_screen_action.triggered.connect(self.toggle_full_screen)
        
        view_menu.addAction(zoom_in_action)
        view_menu.addAction(zoom_out_action)
        view_menu.addSeparator()
        view_menu.addAction(full_screen_action)

        help_menu = menu_bar.addMenu("&Help")
        
        #Help actions

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.about_dialog)
        help_menu.addAction(about_action)
    
    def update_status_bar(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        char_count = len(self.editor.toPlainText())
        
        self.status_label.setText(f"Line: {line}, Col: {col} | Characters: {char_count}")

    def about_dialog(self):
        QMessageBox.about(self, "About NVX Editor",
                            "NVX Text Editor\n"
                            "Built with Python and Qt\n"
                            "Created by Jason Rexhaj\n"
                            "Version 0.2"
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
    
    def new_file(self):
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self, 'Save Changes?',
                "Save current file before creating a new one?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.file_save()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.editor.clear()
        self.current_file = None
        self.setWindowTitle("NVX Editor")

    def file_open(self):
        # Open a text file from filesystem using standard dialog.
        # Sets editor contents and current file path.
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", 
                                             "Text File (*.txt);;All Files (*)")
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
        # Save current document; if not yet named, open Save As dialog.
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
        # Save document to a new filename; supports .txt and .pdf through print pipeline.
        path, _ = QFileDialog.getSaveFileName(
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
            self.editor.print(printer)

    def handle_delete(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        else:
            cursor.deleteChar()
    
    def toggle_full_screen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def find_text(self):
        text, ok = QInputDialog.getText(self, "Find", "Search for:")
        
        if ok and text:
            found = self.editor.find(text)
            
            if not found:
                self.editor.moveCursor(QTextCursor.MoveOperation.Start)
                found = self.editor.find(text)
                
            if not found:
                QMessageBox.information(self, "Find", f"'{text}' not found.")
    

    def load_theme(self, theme_name):
        # Load light or dark style sheet from disk and apply to QApplication.
        base_dir = self.resource_base_path()
        filename = "dark.qss" if theme_name == "Dark" else "light.qss"
        file_path = base_dir / "data" / "styles" / filename

        app = QApplication.instance()
        
        # 1. Clear existing styles to prevent Dark Mode bleeding into Light Mode
        app.setStyleSheet("")

        if theme_name == "Light":
            # 2. Force Fusion style to reset native OS style artifacts
            app.setStyle("Fusion") 
            app.setPalette(app.style().standardPalette())

        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    style_data = f.read()
                    # 3. Apply theme sheet globally across the app
                    app.setStyleSheet(style_data)
            except Exception as e:
                print(f"Error reading stylesheet: {e}")
                
    def get_settings_path(self):
        # Avoid QStandardPaths returning a confusing main.py app path in some environments.
        fallback = Path.home() / ".config" / "nvx_editor"

        config_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation) or "")
        if not config_dir or config_dir.name == "main.py" or config_dir.is_file():
            config_dir = fallback

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "settings.json"

    def load_settings_from_json(self):
        path = self.get_settings_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                
                # Only load Editor font and Theme
                family = config.get("font_family", "Sans-Serif")
                size = config.get("font_size", 12)
                self.editor.setFont(QFont(family, size))

                tab_spacing = int(config.get("tab_spacing", 4))
                space_width = self.editor.fontMetrics().horizontalAdvance(' ')
                self.editor.setTabStopDistance(int(tab_spacing) * space_width)
                
                self.current_theme = config.get("theme", "Light")
                self.load_theme(self.current_theme)
                
                print(f"Settings loaded successfully from {path}")
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings_to_json(self, font, size, theme, tab_spacing):
        config = {
            "font_family": font,
            "font_size": size,
            "theme": theme,
            "tab_spacing": tab_spacing
        }
        try:
            settings_path = self.get_settings_path()
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def reset_to_defaults(self, dialog):
        path = self.get_settings_path()
        
        if os.path.exists(path):
            try:
                os.remove(path)
                print("Settings file deleted. Reverting to defaults.")
            except Exception as e:
                print(f"Error deleting settings: {e}")

        default_font = "Sans-Serif"
        default_size = 12
        self.current_theme = "Light"
        
        self.editor.setFont(QFont(default_font, default_size))
        self.load_theme(self.current_theme)
        
        dialog.accept()

    def show_settings(self):
        current_font = self.editor.font().family()
        current_size = self.editor.font().pointSize()

        current_tab = self.editor.tabStopDistance() / self.editor.fontMetrics().horizontalAdvance(' ')


        dialog = Settings(current_font, current_size, self.current_theme, int(current_tab), self)
        dialog.reset_btn.clicked.connect(lambda: self.reset_to_defaults(dialog))
        
        if hasattr(dialog, 'apply_button') and dialog.apply_button is not None:
            dialog.apply_button.clicked.connect(lambda: self.apply_settings_from_dialog(dialog))

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_settings_from_dialog(dialog)

    def apply_settings_from_dialog(self, dialog):
        new_font = dialog.font_combo.currentText()
        new_size = dialog.font_size_spin.value()
        new_theme = dialog.theme_combo.currentText()
        
        # Apply Editor settings
        self.editor.setFont(QFont(new_font, new_size))

        try:
            tab_stop = int(dialog.tab_size.text() or 4)
        except ValueError:
            tab_stop = 4

        tab_val = tab_stop

        space_width = self.editor.fontMetrics().horizontalAdvance(' ')
        self.editor.setTabStopDistance(tab_stop * space_width)

        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.load_theme(self.current_theme)
        
        self.save_settings_to_json(new_font, new_size, new_theme, tab_val)