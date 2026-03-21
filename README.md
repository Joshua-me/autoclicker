# Python Autoclicker

A simple Python autoclicker with a tiny desktop GUI.

## macOS 11.0+ Compatibility
The macOS build is `app_mac.py` and targets macOS Big Sur (11.0) and newer with Python 3.

Before using the tracker on macOS, grant both Accessibility and Screen Recording permission:

1. Open **System Settings** (or **System Preferences** on older versions).
2. Go to **Privacy & Security > Accessibility**.
3. Enable access for the app launching Python (for example, Terminal, iTerm, or your Python app bundle).
4. Go to **Privacy & Security > Screen Recording**.
5. Enable access for the same app so screenshot-based target tracking can see the screen.

Without these permissions, macOS blocks synthetic mouse clicks, global hotkeys, or screen capture.

## macOS Version

Run it from the repo root with either:

```bash
python3 app_mac.py
```

or:

```bash
python3 autoclicker/app_mac.py
```

## Windows Version
A dedicated Windows build is available in `app_windows.py`.

Run it from the repo root with either:

```bash
python app_windows.py
```

or:

```bash
python autoclicker/app_windows.py
```

Hotkey toggle is **Ctrl+Alt+A** (same as the main app).

## Chromebook / ChromeOS (Linux / Crostini)
A Chromebook-friendly build is available in `app_chromebook.py` and runs inside the Linux development environment.

Run it from the repo root with either:

```bash
python3 app_chromebook.py
```

or:

```bash
python3 autoclicker/app_chromebook.py
```

If global hotkeys or synthetic clicks do not work, use the Start/Stop buttons instead. Some sessions and window managers restrict input hooks.

## Features
- Set click interval in seconds.
- Capture a target under the cursor, then track it across the screen using template matching.
- Start and stop from the app window.
- Toggle start/stop using a global hotkey: **Ctrl+Alt+A**.
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

The repo root `requirements.txt` forwards to `autoclicker/requirements.txt`, so the command works without changing directories.

## Tracking Workflow

1. Hover the mouse over the object you want to follow.
2. Click **Capture Target** to save an `80x80` sample around the cursor.
3. Enable **Track captured target**.
4. Press **Start** or use **Ctrl+Alt+A**.

The app will keep scanning the screen, move the mouse to the best match, and click there on each interval. If the match confidence drops too far, it waits for the object to reappear instead of clicking a random location.

## Notes
- Minimum supported interval is `0.01` seconds.
- Use **Ctrl+Alt+A** to quickly activate/deactivate clicking.
- Tracking works best on distinct UI elements that keep roughly the same appearance and scale.
