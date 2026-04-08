# Contributing to FingerFly

Thanks for your interest in contributing! Here's how to get started.

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/fingerfly.git
cd fingerfly
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

## Project Structure

```
fingerfly/
├── server.py        # Python server (HTTP + WebSocket + mouse control)
├── index.html       # Mobile web UI (single file, no build tools)
├── start.command    # macOS double-click launcher
├── requirements.txt # Python dependencies
└── README.md
```

## Guidelines

- **Keep it simple.** The entire project is two functional files (`server.py` + `index.html`). No build tools, no frameworks, no bundlers. Let's keep it that way.
- **Test on a real phone.** Touch events behave differently on real devices vs. browser dev tools. Always test gesture changes on an actual phone.
- **macOS only (for now).** The server uses the Quartz CoreGraphics API. Linux/Windows support would require platform-specific backends — PRs welcome.

## Areas for Contribution

- **Linux backend** — replace Quartz calls with `xdotool` or `python-xlib`
- **Windows backend** — replace Quartz calls with `pyautogui` or `ctypes` win32 API
- **New gestures** — drag, three-finger drag, zoom
- **Performance** — lower latency WebSocket transport, binary protocol
- **UI polish** — themes, animations, haptic patterns

## Submitting Changes

1. Fork the repo
2. Create a feature branch (`git checkout -b my-feature`)
3. Make your changes
4. Test on a real phone + Mac
5. Submit a pull request

## Code Style

- Python: follow PEP 8, no external linters required
- JavaScript: vanilla JS, no frameworks, inline in `index.html`
- Keep the line count low — simplicity is a feature
