from src.file_manager import File_Manager
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QFileDialog


def test_file_save(tmp_path, editor, fake_app):

    editor.setPlainText("Hello NVX Editor!")
    editor.document().setModified(True)

    file_path = tmp_path / "test.txt"

    fake_app.current_file = str(file_path)

    file_manager = File_Manager(fake_app)

    result = file_manager.file_save()

    assert result is True
    assert file_path.read_text(encoding="utf-8") == "Hello NVX Editor!"
    assert editor.document().isModified() is False


def test_new_file_cancel(editor, monkeypatch, tmp_path, fake_app):

    editor.setPlainText("Unsaved changes")
    editor.document().setModified(True)

    file_path = tmp_path / "notes.txt"

    fake_app.current_file = str(file_path)

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel
    )

    file_manager = File_Manager(fake_app)
    file_manager.new_file()

    assert editor.toPlainText() == "Unsaved changes"
    assert editor.document().isModified() is True
    assert fake_app.current_file == str(file_path)

def test_new_file_save_as_cancel(editor, monkeypatch, fake_app):
    editor.setPlainText("Important unsaved text")
    editor.document().setModified(True)

    file_manager = File_Manager(fake_app)

    # User chooses Save when prompted.
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save
    )

    # User then cancels the Save As dialog.
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: ("", "")
    )

    file_manager.new_file()

    assert editor.toPlainText() == "Important unsaved text"
    assert editor.document().isModified() is True
    assert fake_app.current_file is None