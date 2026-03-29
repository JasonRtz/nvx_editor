import os
import sys
import json
from pathlib import Path
from PyQt6.QtCore import QStandardPaths, QUrl
from PyQt6.QtWidgets import QApplication, QDialog, QInputDialog, QMainWindow, QTextEdit, QMessageBox, QLabel
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont, QTextCursor, QDesktopServices
from .settings import Settings
from .file_manager import File_Manager

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

        # Application icon (.exe bundling via PyInstaller may set _MEIPASS)
        icon_path = os.path.normpath(str(self.resource_base_path() / "data" / "icons" / "nvx_editor.png"))

        self.file_mng = File_Manager(self)

        try:
            icon = QIcon(icon_path)
            if icon.isNull():
                raise ValueError(f"Failed to load icon data: {icon_path}")

            self.setWindowIcon(icon)

        except Exception as e:
            print(f"Could not set window icon ({icon_path}): {e}")

        self.recent_files = [] 

        # Build UI menus and actions        
        self.view()

        # Load saved settings (font + theme) from disk (if present)
        self.load_settings_from_json()

        self.status_bar = self.statusBar()
        self.status_label = QLabel("Line: 1, Col: 1 | Characters: 0")
        self.status_bar.addPermanentWidget(self.status_label)

        self.editor.cursorPositionChanged.connect(self.update_status_bar)

    def view(self):
        menu_bar = self.menuBar()
        
        #File Menu
        file_menu = menu_bar.addMenu("&File")
        self.add_action(file_menu, "&New", self.file_mng.new_file, "Ctrl+N")
        file_menu.addSeparator()
        self.add_action(file_menu, "&Open", self.file_mng.file_open, "Ctrl+O")
        self.recent_menu = file_menu.addMenu("&Recent")
        file_menu.addSeparator()
        self.add_action(file_menu, "&Save", self.file_mng.file_save, "Ctrl+S")
        self.add_action(file_menu, "&Save As", self.file_mng.file_save_as, "Ctrl+Shift+S")
        self.add_action(file_menu, "&Print", self.file_mng.print_file, "Ctrl+P")
        file_menu.addSeparator()
        self.add_action(file_menu, "&Exit", self.close, "Ctrl+Q")
        
        #Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        self.add_action(edit_menu, "&Undo", self.editor.undo, "Ctrl+Z")
        self.add_action(edit_menu, "&Redo", self.editor.redo, "Ctrl+Y")
        edit_menu.addSeparator()
        self.add_action(edit_menu, "&Cut", self.editor.cut, "Ctrl+X")
        self.add_action(edit_menu, "&Copy", self.editor.copy, "Ctrl+C")
        self.add_action(edit_menu, "&Paste", self.editor.paste, "Ctrl+V")
        self.add_action(edit_menu, "&Delete", self.handle_delete, QKeySequence.StandardKey.Delete)
        edit_menu.addSeparator()
        self.add_action(edit_menu, "&Find", self.find_text, "Ctrl+F")
        self.add_action(edit_menu, "&Select All", self.editor.selectAll, "Ctrl+A")
        edit_menu.addSeparator()
        self.add_action(edit_menu, "&Settings", self.show_settings)

        #View Menu
        view_menu = menu_bar.addMenu("&View")
        self.add_action(view_menu, "&Zoom In", self.editor.zoomIn, "Ctrl+=")
        self.add_action(view_menu, "&Zoom Out", self.editor.zoomOut, "Ctrl+-")
        self.add_action(view_menu, "Word Wrap", 
                        lambda checked: self.editor.setLineWrapMode(
                            QTextEdit.LineWrapMode.WidgetWidth if checked else QTextEdit.LineWrapMode.NoWrap),
                            "Alt+Z", True).setChecked(True)
        view_menu.addSeparator()
        self.add_action(view_menu, "&Full Screen", self.toggle_full_screen, "F11")

        #Help Menu
        help_menu = menu_bar.addMenu("&Help")
        self.add_action(help_menu, "Report Issue", self.report_issue)        
        self.add_action(help_menu, "&About", self.about_dialog)

    def add_action(self, menu, text, slot, shortcut=None, checkable=False):
        action = QAction(text, self)
        if shortcut: action.setShortcut(shortcut)
        if checkable: action.setCheckable(True)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action
    
    def update_status_bar(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        char_count = self.editor.document().characterCount()
        
        self.status_label.setText(f"Line: {line}, Col: {col} | Characters: {char_count}")

    def about_dialog(self):
        QMessageBox.about(self, "About NVX Editor",
                            "NVX Text Editor\n"
                            "Built with Python and Qt\n"
                            "Created by Jason Rexhaj\n"
                            "Version 1.0"
        )

    def report_issue(self):
        # Open the project's GitHub issues page in the default browser.
        QDesktopServices.openUrl(QUrl("https://github.com/JasonRtz/nvx_editor/issues"))

    def closeEvent(self, event):
        self.file_mng.handle_close_event(event)

    def update_recent_actions(self):
        self.recent_menu.clear()
        
        for path in self.recent_files:
            action = QAction(os.path.basename(path), self)
            action.setData(path) 
            # Points to the moved function in file_manager
            action.triggered.connect(lambda chk, p=path: self.file_mng.open_recent_file(p))
            self.recent_menu.addAction(action)
        
        if not self.recent_files:
            self.recent_menu.setEnabled(False)
        else:
            self.recent_menu.setEnabled(True)
            self.recent_menu.addSeparator()
            clear_action = QAction("Clear Recently Open", self)
            # Points to the moved function in file_manager
            clear_action.triggered.connect(self.file_mng.clear_recent_files)
            self.recent_menu.addAction(clear_action)

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
        
        # Clear existing styles to prevent Dark Mode bleeding into Light Mode
        app.setStyleSheet("")

        if theme_name == "Light":
            # Force Fusion style to reset native OS style artifacts
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

                self.recent_files = config.get("recent_files", []) #
                self.update_recent_actions()
                
                print(f"Settings loaded successfully from {path}")
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings_to_json(self, font, size, theme, tab_spacing):
        config = {
            "font_family": font,
            "font_size": size,
            "theme": theme,
            "tab_spacing": tab_spacing,
            "recent_files": self.recent_files
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