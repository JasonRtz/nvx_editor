import pytest
from PyQt6.QtWidgets import QTextEdit
from types import SimpleNamespace

@pytest.fixture
def editor(qtbot):
    text_editor = QTextEdit()
    qtbot.addWidget(text_editor)

    return text_editor

@pytest.fixture
def fake_app(editor):
    return SimpleNamespace(
        editor=editor,
        current_file=None,
        setWindowTitle=lambda title: None
    )