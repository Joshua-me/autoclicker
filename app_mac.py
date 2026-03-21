"""macOS autoclicker with template-based mouse tracking for macOS 11+."""

from __future__ import annotations

import platform
import threading
import time
import tkinter as tk
from tkinter import messagebox

MIN_INTERVAL_SECONDS = 0.01
TARGET_CAPTURE_SIZE = 80
MATCH_CONFIDENCE = 0.72
TOGGLE_HOTKEY = "<ctrl>+<alt>+a"
MIN_MACOS_MAJOR = 11

try:
    import cv2
except ModuleNotFoundError as error:
    raise SystemExit(
        "Missing dependency 'opencv-python'. Activate the project virtualenv "
        "or run: pip install -r requirements.txt"
    ) from error

try:
    import numpy as np
except ModuleNotFoundError as error:
    raise SystemExit(
        "Missing dependency 'numpy'. Activate the project virtualenv "
        "or run: pip install -r requirements.txt"
    ) from error

try:
    import pyautogui
except ModuleNotFoundError as error:
    raise SystemExit(
        "Missing dependency 'pyautogui'. Activate the project virtualenv "
        "or run: pip install -r requirements.txt"
    ) from error

try:
    from pynput import keyboard
except ModuleNotFoundError as error:
    raise SystemExit(
        "Missing dependency 'pynput'. Activate the project virtualenv "
        "or run: pip install -r requirements.txt"
    ) from error


def _macos_major_version() -> int:
    version_string = platform.mac_ver()[0]
    if not version_string:
        return 0
    major_text = version_string.split(".", maxsplit=1)[0]
    try:
        return int(major_text)
    except ValueError:
        return 0


class MacAutoClickerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Simple Python Autoclicker (macOS 11+)")
        self.root.resizable(False, False)

        self.running = False
        self.worker_thread: threading.Thread | None = None
        self.hotkey_listener: keyboard.GlobalHotKeys | None = None
        self.interval_var = tk.StringVar(value="0.1")
        self.status_var = tk.StringVar(value="Status: Stopped")
        self.tracking_var = tk.BooleanVar(value=False)
        self.target_status_var = tk.StringVar(value="Target: Not captured")
        self.target_template: np.ndarray | None = None

        self._build_ui()
        self._start_hotkey_listener()

    def _build_ui(self) -> None:
        frame = tk.Frame(self.root, padx=14, pady=14)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Click interval (seconds):").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.interval_var, width=10).grid(
            row=0, column=1, padx=(8, 0), sticky="w"
        )

        self.capture_button = tk.Button(
            frame,
            text="Capture Target",
            width=12,
            command=self.capture_target,
        )
        self.capture_button.grid(row=1, column=0, pady=(12, 0), sticky="w")

        tk.Checkbutton(
            frame,
            text="Track captured target",
            variable=self.tracking_var,
            onvalue=True,
            offvalue=False,
        ).grid(row=1, column=1, pady=(12, 0), sticky="w")

        self.start_button = tk.Button(frame, text="Start", width=12, command=self.start)
        self.start_button.grid(row=2, column=0, pady=(12, 0), sticky="w")

        self.stop_button = tk.Button(
            frame,
            text="Stop",
            width=12,
            command=self.stop,
            state="disabled",
        )
        self.stop_button.grid(row=2, column=1, pady=(12, 0), sticky="w")

        tk.Label(
            frame,
            textvariable=self.target_status_var,
            fg="#555",
            wraplength=380,
            justify="left",
        ).grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="w")

        tk.Label(
            frame,
            text=f"Toggle hotkey: {TOGGLE_HOTKEY}",
            fg="#555",
            wraplength=380,
            justify="left",
        ).grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="w")

        tk.Label(
            frame,
            text=(
                "Hover the object to capture it, then enable tracking to follow it "
                "across the screen while clicking."
            ),
            fg="#555",
            wraplength=380,
            justify="left",
        ).grid(row=5, column=0, columnspan=2, pady=(6, 0), sticky="w")

        tk.Label(
            frame,
            text=(
                "macOS 11+: enable Accessibility for clicks/hotkeys and Screen Recording "
                "for screenshots in System Settings -> Privacy & Security."
            ),
            fg="#555",
            wraplength=380,
            justify="left",
        ).grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="w")

        tk.Label(frame, textvariable=self.status_var).grid(
            row=7, column=0, columnspan=2, pady=(12, 0), sticky="w"
        )

    def _start_hotkey_listener(self) -> None:
        try:
            self.hotkey_listener = keyboard.GlobalHotKeys(
                {
                    TOGGLE_HOTKEY: self._on_hotkey_pressed,
                }
            )
            self.hotkey_listener.start()
        except Exception as error:
            messagebox.showwarning(
                "Hotkey unavailable",
                (
                    "Global hotkey could not be started.\n"
                    "You can still use Start/Stop buttons.\n\n"
                    f"Details: {error}"
                ),
            )

    def _on_hotkey_pressed(self) -> None:
        self.root.after(0, self.toggle)

    def toggle(self) -> None:
        if self.running:
            self.stop()
        else:
            self.start()

    def _handle_runtime_error(self, title: str, error: Exception) -> None:
        self.stop()
        messagebox.showerror(title, f"Stopped due to an error:\n{error}")

    def _screen_to_gray(self, screenshot) -> np.ndarray:
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    def _find_target_center(self) -> tuple[int, int] | None:
        if self.target_template is None:
            return None

        screenshot = pyautogui.screenshot()
        screen_gray = self._screen_to_gray(screenshot)
        result = cv2.matchTemplate(screen_gray, self.target_template, cv2.TM_CCOEFF_NORMED)
        _, max_value, _, max_location = cv2.minMaxLoc(result)
        if max_value < MATCH_CONFIDENCE:
            return None

        template_height, template_width = self.target_template.shape
        center_x = max_location[0] + template_width // 2
        center_y = max_location[1] + template_height // 2
        return center_x, center_y

    def capture_target(self) -> None:
        try:
            x, y = pyautogui.position()
            half_size = TARGET_CAPTURE_SIZE // 2
            screen_width, screen_height = pyautogui.size()
            width = min(TARGET_CAPTURE_SIZE, screen_width)
            height = min(TARGET_CAPTURE_SIZE, screen_height)
            left = max(0, min(x - half_size, screen_width - width))
            top = max(0, min(y - half_size, screen_height - height))
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            self.target_template = self._screen_to_gray(screenshot)
            self.target_status_var.set(
                f"Target: Captured {width}x{height} area around ({x}, {y})"
            )
        except Exception as error:
            messagebox.showerror(
                "Target capture failed",
                (
                    "Could not capture the screen region.\n"
                    "On macOS 11+, verify Screen Recording permission for the app running Python.\n\n"
                    f"Details: {error}"
                ),
            )

    def _click_loop(self, interval: float) -> None:
        try:
            while self.running:
                if self.tracking_var.get():
                    target_center = self._find_target_center()
                    if target_center is None:
                        self.root.after(
                            0,
                            lambda: self.status_var.set("Status: Running (target not found)"),
                        )
                        time.sleep(interval)
                        continue

                    pyautogui.moveTo(*target_center)
                    self.root.after(
                        0,
                        lambda x=target_center[0], y=target_center[1]: self.status_var.set(
                            f"Status: Running (tracking at {x}, {y})"
                        ),
                    )

                pyautogui.click()
                time.sleep(interval)
        except Exception as error:
            self.root.after(0, lambda: self._handle_runtime_error("Autoclicker stopped", error))

    def start(self) -> None:
        if self.running:
            return

        try:
            interval = float(self.interval_var.get())
            if interval < MIN_INTERVAL_SECONDS:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid interval",
                f"Please enter a number greater than or equal to {MIN_INTERVAL_SECONDS:.2f}.",
            )
            return

        if self.tracking_var.get() and self.target_template is None:
            messagebox.showerror("Target required", "Capture a target before enabling tracking.")
            return

        mode = "tracking + clicking" if self.tracking_var.get() else "clicking"
        self.running = True
        self.status_var.set(f"Status: Running ({mode} every {interval:.3f}s)")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.capture_button.config(state="disabled")

        self.worker_thread = threading.Thread(
            target=self._click_loop,
            args=(interval,),
            daemon=True,
        )
        self.worker_thread.start()

    def stop(self) -> None:
        self.running = False
        self.status_var.set("Status: Stopped")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.capture_button.config(state="normal")

    def shutdown(self) -> None:
        self.stop()
        if self.hotkey_listener is not None:
            self.hotkey_listener.stop()


if __name__ == "__main__":
    if platform.system() != "Darwin":
        raise SystemExit("app_mac.py is intended to run on macOS only.")

    if _macos_major_version() < MIN_MACOS_MAJOR:
        raise SystemExit("app_mac.py requires macOS 11.0 or newer.")

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0

    try:
        root = tk.Tk()
    except tk.TclError as error:
        raise SystemExit(
            "Unable to start the Tk GUI. Run this app from a macOS desktop session "
            "with windowing access enabled.\n"
            f"Details: {error}"
        ) from error

    app = MacAutoClickerApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.shutdown(), root.destroy()))
    root.mainloop()
