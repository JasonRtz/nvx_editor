# NVX Editor

<div align="center">
  <img src="https://github.com/user-attachments/assets/1e39562d-e194-4e47-9ce1-64f08aadb1e5" width="128" height="128" alt="NVX Editor Logo">
  <p><i>A sleek, lightweight text editor built with Python and Qt.</i></p>
</div>

---


## Overview

NVX Editor is a desktop text editor built with Python and PyQt6.

It provides a straightforward interface for creating and editing plain-text files, with customizable appearance, file management, and essential editing tools.

## Features

## Screenshots

### Light Theme

![NVX Editor - Light Theme](assets/screenshots/light-theme.png)

### Dark Theme

![NVX Editor - Dark Theme](assets/screenshots/dark-theme.png)

### File Management
- Create, open, and save plain-text files.
- Access recently opened files.
- Print documents.
- Receive warnings before discarding unsaved changes.

### Text Editing
- Undo and redo changes.
- Cut, copy, paste, and delete text.
- Find text within a document.
- Enable or disable word wrapping.
- Zoom in and out.

### Customization
- Light and Dark themes.
- Customizable font family and size.
- Adjustable tab spacing.
- Persistent application settings.

### User Interface
- Full-screen mode.
- Status bar displaying line, column, and character count.
- Keyboard shortcuts for common actions.

## Requirements

- Python 3
- PyQt6

## Requirements

- Python 3
- PyQt6

## Installation

### Windows

1. Clone the repository:

   ```powershell
   git clone https://github.com/JasonRtz/nvx_editor.git
   cd nvx_editor
   ```

2. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

3. Install dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Run the application:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

### Linux

1. Clone the repository:

   ```bash
   git clone https://github.com/JasonRtz/nvx_editor.git
   cd nvx_editor
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

3. Install dependencies:

   ```bash
   .venv/bin/python -m pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   .venv/bin/python main.py
   ```

**Note:** Some Linux distributions may require additional system packages for Python virtual environments or Qt.


## Running Tests

Install development dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Run the automated tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## License

NVX Editor is free and open-source software licensed under the GNU General Public License v3.0 (GPL-3.0).

You are free to use, modify, and redistribute the software under the terms of this license.

See the [LICENSE](LICENSE) file for the full license text.
