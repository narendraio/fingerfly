#!/bin/bash
# FingerFly — double-click this file to start
# ─────────────────────────────────────────────

cd "$(dirname "$0")"

clear
cat << 'BANNER'

   ███████╗██╗███╗   ██╗ ██████╗ ███████╗██████╗ ███████╗██╗  ██╗   ██╗
   ██╔════╝██║████╗  ██║██╔════╝ ██╔════╝██╔══██╗██╔════╝██║  ╚██╗ ██╔╝
   █████╗  ██║██╔██╗ ██║██║  ███╗█████╗  ██████╔╝█████╗  ██║   ╚████╔╝
   ██╔══╝  ██║██║╚██╗██║██║   ██║██╔══╝  ██╔══██╗██╔══╝  ██║    ╚██╔╝
   ██║     ██║██║ ╚████║╚██████╔╝███████╗██║  ██║██║     ███████╗██║
   ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝

   Your phone is your trackpad.

BANNER

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "  ✗ Python 3 not found."
    echo "    Install from: https://www.python.org/downloads/"
    echo ""
    echo "  Press any key to exit..."
    read -n1
    exit 1
fi
echo "  ✓ Python 3 found: $(python3 --version)"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "  → Creating virtual environment..."
    python3 -m venv venv
    echo "  ✓ Virtual environment created"
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if ! python3 -c "import websockets" &>/dev/null; then
    echo "  → Installing websockets..."
    pip install websockets -q
    echo "  ✓ websockets installed"
fi

if ! python3 -c "import qrcode" &>/dev/null; then
    echo "  → Installing qrcode..."
    pip install qrcode -q
    echo "  ✓ qrcode installed"
fi

if ! python3 -c "import Quartz" &>/dev/null; then
    echo "  → Installing pyobjc-framework-Quartz..."
    pip install pyobjc-framework-Quartz -q
    echo "  ✓ Quartz framework installed"
fi

echo ""
echo "  ─────────────────────────────────────────────"
echo "  Starting FingerFly..."
echo ""

# Run the server
python3 server.py

echo ""
echo "  FingerFly stopped. Press any key to close."
read -n1
