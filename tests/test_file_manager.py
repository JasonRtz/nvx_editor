from src.file_manager import File_Manager
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QCloseEvent


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

def test_open_recent_file_cancel(tmp_path, editor, fake_app, monkeypatch):
    # Create a file that we will attempt to open.
    new_file = tmp_path / "another.txt"
    new_file.write_text("Content from another file", encoding="utf-8")

    # Simulate the currently opened document.
    current_file = tmp_path / "current.txt"
    fake_app.current_file = str(current_file)

    editor.setPlainText("Important unsaved changes")
    editor.document().setModified(True)

    # Simulate the user selecting Cancel.
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel
    )

    file_manager = File_Manager(fake_app)
    file_manager.open_recent_file(str(new_file))

    # Verify that nothing has changed.
    assert editor.toPlainText() == "Important unsaved changes"
    assert editor.document().isModified() is True
    assert fake_app.current_file == str(current_file)

def test_open_recent_file_discard(tmp_path, editor, fake_app, monkeypatch):
    # Create the file we want to open.
    new_file = tmp_path / "another.txt"
    new_file.write_text("New file content", encoding="utf-8")

    # Simulate a document with unsaved changes.
    fake_app.current_file = str(tmp_path / "current.txt")

    editor.setPlainText("Unsaved changes")
    editor.document().setModified(True)

    # Simulate selecting Discard.
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Discard
    )

    file_manager = File_Manager(fake_app)

    # Record recent-file updates without needing the full application.
    recent_updates = []
    monkeypatch.setattr(
        file_manager,
        "update_recent_files",
        lambda path: recent_updates.append(path)
    )

    file_manager.open_recent_file(str(new_file))

    assert editor.toPlainText() == "New file content"
    assert editor.document().isModified() is False
    assert fake_app.current_file == str(new_file)
    assert recent_updates == [str(new_file)]

def test_open_recent_file_save(tmp_path, editor, fake_app, monkeypatch):
    # Create the current file.
    current_file = tmp_path / "current.txt"
    current_file.write_text("Original content", encoding="utf-8")

    # Create the file we want to open.
    new_file = tmp_path / "another.txt"
    new_file.write_text("Another file content", encoding="utf-8")

    # Simulate unsaved changes.
    fake_app.current_file = str(current_file)

    editor.setPlainText("Updated content")
    editor.document().setModified(True)

    # Simulate selecting Save.
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save
    )

    file_manager = File_Manager(fake_app)

    monkeypatch.setattr(
        file_manager,
        "update_recent_files",
        lambda path: None
    )

    file_manager.open_recent_file(str(new_file))

    # Verify the previous document was saved.
    assert current_file.read_text(encoding="utf-8") == "Updated content"

    # Verify the new document was opened.
    assert editor.toPlainText() == "Another file content"
    assert editor.document().isModified() is False
    assert fake_app.current_file == str(new_file)

def test_open_recent_file_save_failure(
    tmp_path, editor, fake_app, monkeypatch
):
    current_file = tmp_path / "current.txt"
    current_file.write_text("Original content", encoding="utf-8")

    new_file = tmp_path / "another.txt"
    new_file.write_text("Another file content", encoding="utf-8")

    fake_app.current_file = str(current_file)

    editor.setPlainText("Important unsaved changes")
    editor.document().setModified(True)

    # User chooses Save.
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save
    )

    file_manager = File_Manager(fake_app)

    # Simulate a failed save operation.
    monkeypatch.setattr(
        file_manager,
        "file_save",
        lambda: False
    )

    recent_updates = []
    monkeypatch.setattr(
        file_manager,
        "update_recent_files",
        lambda path: recent_updates.append(path)
    )

    file_manager.open_recent_file(str(new_file))

    # Original document must remain unchanged.
    assert editor.toPlainText() == "Important unsaved changes"
    assert editor.document().isModified() is True
    assert fake_app.current_file == str(current_file)

    # No changes should have been saved to disk.
    assert current_file.read_text(encoding="utf-8") == "Original content"

    # Recent files must not be updated.
    assert recent_updates == []

def test_close_event_save_failure(editor, fake_app, monkeypatch):
    # Simulate unsaved changes.
    editor.setPlainText("Important unsaved text")
    editor.document().setModified(True)

    # User chooses Save.
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save
    )

    file_manager = File_Manager(fake_app)

    # Simulate a failed save operation.
    monkeypatch.setattr(
        file_manager,
        "file_save",
        lambda: False
    )

    # Simulate a window close event.
    event = QCloseEvent()

    file_manager.handle_close_event(event)

    # Closing must be rejected.
    assert event.isAccepted() is False

    # Unsaved content must remain intact.
    assert editor.toPlainText() == "Important unsaved text"
    assert editor.document().isModified() is True

def test_close_event_cancel(editor, fake_app, monkeypatch):
    editor.setPlainText("Unsaved changes")
    editor.document().setModified(True)

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel
    )

    file_manager = File_Manager(fake_app)

    event = QCloseEvent()
    file_manager.handle_close_event(event)

    assert event.isAccepted() is False
    assert editor.toPlainText() == "Unsaved changes"
    assert editor.document().isModified() is True

def test_close_event_save_success(editor, fake_app, monkeypatch):
    editor.setPlainText("Important text")
    editor.document().setModified(True)

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save
    )

    file_manager = File_Manager(fake_app)

    monkeypatch.setattr(
        file_manager,
        "file_save",
        lambda: True
    )

    event = QCloseEvent()
    event.ignore()

    file_manager.handle_close_event(event)

    assert event.isAccepted() is True