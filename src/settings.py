from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QPushButton, QSpinBox, QVBoxLayout

class Settings(QDialog):
    # Settings dialog for editor font, size, theme, and tab spacing.
    # Uses QDialog buttons to accept or cancel changes.
    def __init__(self, current_font, current_size, current_theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "Sans-Serif", 
            "Serif", 
            "Monospace",
            "System-UI", 
            "Liberation Mono", 
            "DejaVu Sans Mono"
        ])
        self.font_combo.setCurrentText(current_font)
        form_layout.addRow("Editor Font:", self.font_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)  
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

        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_defaults)
        layout.addWidget(self.reset_btn)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # Expose the apply button so the main app can connect to it
        self.apply_button = buttons.button(QDialogButtonBox.StandardButton.Apply)

        layout.addWidget(buttons)

    def reset_defaults(self):
        # Switch UI values back to safe defaults.
        self.font_combo.setCurrentText("Courier New")
        self.font_size_spin.setValue(12)
        self.theme_combo.setCurrentText("Light")
        self.tab_size.setText("4")