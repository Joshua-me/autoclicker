# Python Autoclicker

A simple Python autoclicker with a tiny desktop GUI.

## macOS 11.0+ Compatibility
This app works on macOS Big Sur (11.0) and newer with Python 3.

Before using the autoclicker on macOS, grant Accessibility permission:

1. Open **System Settings** (or **System Preferences** on older versions).
2. Go to **Privacy & Security > Accessibility**.
3. Enable access for the app launching Python (for example, Terminal, iTerm, or your Python app bundle).

Without this permission, macOS blocks synthetic mouse clicks and global hotkeys.

## Windows Version
A dedicated Windows build is available in `app_windows.py`.

Run it on Windows with:

```bash
python app_windows.py
```

Hotkey toggle is **Ctrl+Alt+A** (same as the main app).

## Chromebook / ChromeOS (Linux / Crostini)
A Chromebook-friendly build is available in `app_chromebook.py` and runs inside the Linux development environment.

Run it on ChromeOS with:

```bash
python3 app_chromebook.py
```

If global hotkeys or synthetic clicks do not work, use the Start/Stop buttons instead. Some sessions and window managers restrict input hooks.

## Features
- Set click interval in seconds.
- Start and stop from the app window.
- Toggle start/stop using a global hotkey: **Ctrl+Alt+A**.
- Uses your current mouse cursor position.
- PyAutoGUI failsafe is enabled (move mouse to top-left corner to trigger failsafe exception).

## Setup

1. Create and activate a virtual environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python3 app.py
```

## Notes
- Minimum supported interval is `0.01` seconds.
- Use **Ctrl+Alt+A** to quickly activate/deactivate clicking.
