# FingerFly

**Turn your phone into a wireless trackpad for your Mac.**

No app to install. No Bluetooth. Just your phone's browser and WiFi.

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS-blue" alt="macOS">
  <img src="https://img.shields.io/badge/python-3.8+-yellow" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/phone-any%20browser-orange" alt="Any Browser">
</p>

---

## How It Works

```
Phone (Safari/Chrome)  ──WiFi──►  Mac (Python Server)
     touch deltas                    moves cursor
     via WebSocket                   via macOS Quartz API
```

Your phone's browser captures touch events and streams them over WebSocket to a lightweight Python server on your Mac, which translates them into native cursor movements, clicks, and system gestures.

---

## Quick Start

### Option A: Double-click (easiest)

1. Double-click **`start.command`** in Finder
2. It auto-installs everything and starts the server
3. Scan the QR code with your phone camera
4. Done.

### Option B: Terminal

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/fingerfly.git
cd fingerfly

# Create venv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python server.py
```

Scan the QR code shown in the terminal, or open the printed URL on your phone.

### Grant Accessibility Permission

**Required on first run.** Without this, macOS blocks programmatic mouse control.

> **System Settings → Privacy & Security → Accessibility** → enable your **Terminal app**

---

## Gestures

| Gesture | Action |
|---|---|
| 1-finger swipe | Move cursor |
| Tap | Left click |
| 2-finger tap | Right click |
| 2-finger swipe | Scroll (natural) |
| 3-finger swipe up | Mission Control |
| 3-finger swipe down | App Expose |
| 3-finger swipe left/right | Switch Spaces |
| 4-finger pinch in | Launchpad |
| 4-finger spread out | Show Desktop |

Plus on-screen **Left Click** and **Right Click** buttons.

---

## Settings

Tap the **gear icon** on the phone UI to adjust:

- **Sensitivity** — cursor speed (0.5x to 5x)
- **Scroll Speed** — scroll multiplier (0.1x to 3x)
- **Tap to Click** — toggle tap detection on/off

---

## Architecture

```
fingerfly/
├── server.py        # Python server (HTTP + WebSocket + macOS mouse control)
├── index.html       # Mobile web UI (single file, served to phone)
├── start.command    # macOS double-click launcher (auto-setup)
├── requirements.txt # Python dependencies
├── LICENSE          # MIT
├── CONTRIBUTING.md  # Contribution guidelines
├── .gitignore
└── README.md
```

**server.py** does three things:
1. **HTTP server** (port 8080) — serves `index.html` to the phone
2. **WebSocket server** (port 8081) — receives touch events in real-time
3. **Mouse control** — translates deltas into cursor movement via macOS Quartz API

**index.html** is a single self-contained file (HTML + CSS + JS) that:
- Captures multi-touch events on the phone
- Streams deltas over WebSocket at 60fps with EMA smoothing
- Detects gestures (tap, scroll, 3-finger swipe, 4-finger pinch)
- Provides a dark, minimal UI with visual touch feedback

---

## Requirements

- **macOS** (uses Quartz CoreGraphics for mouse control)
- **Python 3.8+**
- **Any phone** with a modern browser (Safari, Chrome, Firefox)
- Both devices on the **same WiFi network**

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Can't connect from phone | Ensure both devices are on the same WiFi. Check that no firewall blocks ports 8080/8081. |
| Cursor doesn't move | Grant Accessibility permission to your terminal app, then restart the server. |
| Gestures not triggering | Enable keyboard shortcuts in **System Settings → Keyboard → Keyboard Shortcuts → Mission Control**. |
| High latency | Move closer to your router. Reduce other network traffic. |
| Page zooms on phone | Touch the trackpad area, not the browser chrome. |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the venv. |
| Port already in use | Kill the old process: `lsof -ti:8080 | xargs kill -9` |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and guidelines.

Areas where help is welcome:
- Linux / Windows backends
- New gestures (drag, zoom, rotate)
- Performance optimizations
- UI themes

---

## License

[MIT](LICENSE) — do whatever you want with it.
