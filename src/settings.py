from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QSpinBox, QVBoxLayout

class Settings(QDialog):
    def __init__(self, current_font, current_size, current_theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.font_combo = QComboBox()
        self.font_combo.addItems(["Courier New", "Arial", "Verdana", "Times New Roman"])
        self.font_combo.setCurrentText(current_font)
        form_layout.addRow("Editor Font:", self.font_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)  # Minimum and maximum font size
        self.font_size_spin.setValue(current_size)
        form_layout.addRow("Editor Font Size:", self.font_size_spin)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(current_theme)
        form_layout.addRow("Theme:", self.theme_combo)

        self.tab_size = QLineEdit()
        self.tab_size.setPlaceholderText("4")
        form_layout.addRow("Tab Spacing:", self.tab_size)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)