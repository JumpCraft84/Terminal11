# Terminal 11 Ultimate 🖥️

A Windows 11-inspired **Python/Tkinter desktop simulator** for **Raspberry Pi 4** and **Windows**. Includes a fullscreen desktop, Start menu, file tools, games, and a **built-in command runner**.

> **Not Microsoft Windows and not a standalone operating system.** Terminal 11 runs on top of Raspberry Pi OS Desktop or Windows. The Raspberry Pi version is **not yet a bootable `.img`**.

## Features

- Fullscreen desktop, centered taskbar, clock, Start menu and search
- File Explorer, Notepad, Code Maker, Calculator, Paint, Sticky Notes, Calendar, Clock
- Settings and theme options, Task Manager-style tools, browser launcher
- Game Maker, Snake and Tic-Tac-Toe
- Built-in terminal/command runner (works with normal commands; **not** an interactive PTY emulator)
- User settings stored under `~/.terminal11/`

## Raspberry Pi 4 installation

Use **Raspberry Pi OS with Desktop (64-bit)**, not Raspberry Pi OS Lite.

1. Open a terminal and install Python/Tkinter:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-tk
   ```
2. Download this repository (green **Code → Download ZIP**) and extract it, or clone it:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Terminal11-Ultimate.git
   cd Terminal11-Ultimate
   ```
   Replace `YOUR-USERNAME` with the actual repository owner after publishing. If Git isn't installed, run `sudo apt install -y git`.
3. Start Terminal 11:
   ```bash
   python3 terminal11.py
   ```

You can also run `bash run-pi.sh` from the repository directory.

## Windows installation

1. Install Python 3 with Tkinter (normally included in the official Windows Python installer).
2. Click **Code → Download ZIP**, extract the ZIP, and open a terminal in the extracted folder.
3. Run:
   ```powershell
   py terminal11.py
   ```
   Or double-click `run-windows.bat`.

## Keyboard shortcuts

- **F11:** Toggle fullscreen
- **Esc:** Leave fullscreen
- **Ctrl+Q:** Quit
- **Ctrl+Alt+S:** Open Start menu (where supported)
- **Ctrl+Alt+T:** Open terminal (where supported)

## Important notes

- The built-in terminal runs **real commands on your computer**. Only enter commands you trust.
- GUI apps require a graphical desktop session; SSH-only/headless setups are not supported without a display server.
- This project has not yet been hardware-tested on every Raspberry Pi OS version.
- Some features may depend on OS-specific utilities and behave differently on Windows and Linux.
- There are no third-party Python packages required for the base application.

## Project layout

```text
Terminal11-Ultimate/
├── terminal11.py          # Main desktop application
├── run-pi.sh              # Raspberry Pi/Linux launcher
├── run-windows.bat        # Windows launcher
├── README.md              # This guide
├── CONTRIBUTING.md        # Contribution guidelines
└── .gitignore             # Ignore generated files
```

## Contributing

Bug reports, feature ideas, and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

No open-source license has been selected yet. Until one is added, normal copyright restrictions apply. The repository owner can add a license through GitHub's **Add file → Create new file → LICENSE** flow.


## Built-in web browser

The **Browser** app now displays web pages inside Terminal 11 with an address/search bar, back, forward, reload, home and external-browser controls. It uses the optional `tkinterweb` HTML renderer. **This is not a full Chrome/Firefox engine**: many JavaScript-heavy websites, streaming services, and sign-in flows will not work. Use **External** for those sites.

### Windows

```cmd
py -m pip install -r requirements.txt
py terminal11.py
```

### Raspberry Pi OS Desktop

```bash
cd Terminal11-Ultimate
bash install-pi-browser.sh
./run-pi.sh
```

A graphical desktop session and internet connection are required. The installer creates a `.venv` directory; do not commit that directory to GitHub.
