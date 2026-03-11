"""Simple GUI autoclicker application with macOS-friendly behavior."""

from __future__ import annotations

import platform
import threading
import time
import tkinter as tk
from tkinter import messagebox

import pyautogui
from pynput import keyboard

TOGGLE_HOTKEY = "<ctrl>+<alt>+a"


class AutoClickerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Simple Python Autoclicker")
        self.root.resizable(False, False)

        self.running = False
        self.worker_thread: threading.Thread | None = None
        self.hotkey_listener: keyboard.GlobalHotKeys | None = None
        self.interval_var = tk.StringVar(value="0.1")
        self.status_var = tk.StringVar(value="Status: Stopped")

        self._build_ui()
        self._start_hotkey_listener()

    def _build_ui(self) -> None:
        frame = tk.Frame(self.root, padx=14, pady=14)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Click interval (seconds):").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.interval_var, width=10).grid(
            row=0, column=1, padx=(8, 0), sticky="w"
        )

        self.start_button = tk.Button(frame, text="Start", width=12, command=self.start)
        self.start_button.grid(row=1, column=0, pady=(12, 0), sticky="w")

        self.stop_button = tk.Button(
            frame,
            text="Stop",
            width=12,
            command=self.stop,
            state="disabled",
        )
        self.stop_button.grid(row=1, column=1, pady=(12, 0), sticky="w")

        tk.Label(
            frame,
            text=f"Toggle hotkey: {TOGGLE_HOTKEY}",
            fg="#555",
            wraplength=320,
            justify="left",
        ).grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")

        tk.Label(
            frame,
            text="Tip: Move your cursor to the target area before activating.",
            fg="#555",
            wraplength=320,
            justify="left",
        ).grid(row=3, column=0, columnspan=2, pady=(6, 0), sticky="w")

        if platform.system() == "Darwin":
            tk.Label(
                frame,
                text=(
                    "macOS: enable Accessibility for Terminal/Python in\n"
                    "System Settings → Privacy & Security → Accessibility."
                ),
                fg="#555",
                wraplength=320,
                justify="left",
            ).grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="w")
            status_row = 5
        else:
            status_row = 4

        tk.Label(frame, textvariable=self.status_var).grid(
            row=status_row, column=0, columnspan=2, pady=(12, 0), sticky="w"
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
                    f"You can still use Start/Stop buttons.\n\nDetails: {error}"
                ),
            )

    def _on_hotkey_pressed(self) -> None:
        self.root.after(0, self.toggle)

    def toggle(self) -> None:
        if self.running:
            self.stop()
        else:
            self.start()

    def _handle_clicking_error(self, error: Exception) -> None:
        self.stop()
        messagebox.showerror(
            "Autoclicker stopped",
            f"Clicking stopped due to an error:\n{error}",
        )

    def _click_loop(self, interval: float) -> None:
        try:
            while self.running:
                pyautogui.click()
                time.sleep(interval)
        except Exception as error:  # keep UI alive and show user-friendly failure info
            self.root.after(0, lambda: self._handle_clicking_error(error))

    def start(self) -> None:
        if self.running:
            return

        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid interval", "Please enter a number greater than 0.")
            return

        self.running = True
        self.status_var.set(f"Status: Running (every {interval:.3f}s)")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

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

    def shutdown(self) -> None:
        self.stop()
        if self.hotkey_listener is not None:
            self.hotkey_listener.stop()


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0

    root = tk.Tk()
    app = AutoClickerApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.shutdown(), root.destroy()))
    root.mainloop()
