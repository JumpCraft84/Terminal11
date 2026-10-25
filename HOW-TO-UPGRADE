# Terminal 11 Ultimate — Chromium Browser Upgrade

This is the uploaded Terminal 11 desktop, with its `tkinterweb` browser replaced by a **Qt WebEngine (Chromium-based)** browser. It opens in its own native window, launched from Terminal 11's Browser app. It is not embedded in a Tkinter widget, because Tkinter cannot directly host Qt WebEngine reliably.

## Windows 10/11

1. Install Python from python.org (64-bit recommended).
2. Extract all files into one folder. Keep `terminal11.py` and `terminal11_browser.py` together.
3. Open Command Prompt in that folder and run:

   ```cmd
   py -m pip install -r requirements.txt
   py terminal11.py
   ```

4. In Terminal 11, open Start > Browser.

## Raspberry Pi 4 / Raspberry Pi OS Desktop (64-bit)

The desktop requires Tkinter. **Qt WebEngine installation on ARM Linux is distribution-dependent**. PySide6's PyPI wheels may not be available for your Pi's Python/architecture. Check your OS repositories first:

```bash
sudo apt update
sudo apt install python3-tk
apt-cache policy python3-pyside6.qtwebenginewidgets python3-pyqt6.qtwebenginewidgets
```

This project currently uses **PySide6**, so the `python3-pyside6.qtwebenginewidgets` package is the compatible system package if offered by your Raspberry Pi OS release. If available, install it and any required Qt packages with apt. Otherwise try a Python environment with a compatible PySide6 wheel; do not assume `pip install PySide6` will work on Pi 4. The browser remains untested on physical Raspberry Pi hardware.

Run the desktop with `python3 terminal11.py` using the Python environment where PySide6 is installed.

## Features

- Chromium-based JavaScript and CSS support
- Tabs, back, forward, refresh, home, search/address bar
- Bookmarks saved under `~/.terminal11/browser/`
- Download prompts and save locations
- Popup/new-window links open as tabs

Modern sites such as Infinite Craft should be much more compatible than with tkinterweb, but some websites may still fail due to hardware limitations, DRM, site restrictions, or graphics drivers.

## Troubleshooting

If you see `No module named PySide6`, install the dependency for the same Python interpreter you use to run Terminal 11.

If the browser opens as a separate window, that is expected. It is a native Qt browser launched by the Tkinter desktop.
