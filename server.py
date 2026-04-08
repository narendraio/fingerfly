#!/usr/bin/env python3
"""FingerFly — turn your phone into a wireless trackpad for macOS."""

import asyncio
import http.server
import json
import os
import socket
import socketserver
import threading

import websockets

# macOS Quartz framework for mouse control
import subprocess

from Quartz.CoreGraphics import (
    CGDisplayPixelsWide,
    CGDisplayPixelsHigh,
    CGEventCreate,
    CGEventCreateMouseEvent,
    CGEventCreateScrollWheelEvent,
    CGEventGetLocation,
    CGEventPost,
    CGMainDisplayID,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGEventMouseMoved,
    kCGEventRightMouseDown,
    kCGEventRightMouseUp,
    kCGHIDEventTap,
    kCGScrollEventUnitPixel,
)

HTTP_PORT = 8080
WS_PORT = 8081

sensitivity = 2.0
scroll_speed = 1.0

# Fractional scroll accumulator (scroll events need integers but we get floats)
scroll_accum_x = 0.0
scroll_accum_y = 0.0


def get_local_ip():
    """Get the local IP address of this machine on the WiFi network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def get_cursor_position():
    """Return the current (x, y) of the mouse cursor."""
    event = CGEventCreate(None)
    loc = CGEventGetLocation(event)
    return loc.x, loc.y


def get_screen_bounds():
    """Return (width, height) of the main display."""
    display_id = CGMainDisplayID()
    w = CGDisplayPixelsWide(display_id)
    h = CGDisplayPixelsHigh(display_id)
    return w, h


def accelerate(delta):
    """Apply acceleration curve: small movements stay precise, fast swipes go further."""
    mag = abs(delta)
    if mag < 1:
        return delta * 0.6
    elif mag < 4:
        return delta * 1.0
    elif mag < 10:
        return delta * 1.4
    else:
        return delta * 1.8


def move_mouse(dx, dy):
    """Move the mouse cursor by (dx, dy) pixels with acceleration, clamped to screen."""
    cx, cy = get_cursor_position()
    sw, sh = get_screen_bounds()
    ax = accelerate(dx) * sensitivity
    ay = accelerate(dy) * sensitivity
    nx = max(0, min(sw - 1, cx + ax))
    ny = max(0, min(sh - 1, cy + ay))
    event = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (nx, ny), 0)
    CGEventPost(kCGHIDEventTap, event)


def click():
    """Perform a left click at the current cursor position."""
    pos = get_cursor_position()
    down = CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, pos, 0)
    up = CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, pos, 0)
    CGEventPost(kCGHIDEventTap, down)
    CGEventPost(kCGHIDEventTap, up)


def right_click():
    """Perform a right click at the current cursor position."""
    pos = get_cursor_position()
    down = CGEventCreateMouseEvent(None, kCGEventRightMouseDown, pos, 1)
    up = CGEventCreateMouseEvent(None, kCGEventRightMouseUp, pos, 1)
    CGEventPost(kCGHIDEventTap, down)
    CGEventPost(kCGHIDEventTap, up)


def scroll(dx, dy):
    """Scroll by (dx, dy) with sub-pixel accumulation for smooth slow scrolls."""
    global scroll_accum_x, scroll_accum_y
    scroll_accum_x += dx * scroll_speed
    scroll_accum_y += dy * scroll_speed
    # Only fire when we've accumulated at least 1 pixel
    sx = int(scroll_accum_x)
    sy = int(scroll_accum_y)
    if sx == 0 and sy == 0:
        return
    scroll_accum_x -= sx
    scroll_accum_y -= sy
    event = CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 2, sy, sx)
    CGEventPost(kCGHIDEventTap, event)


def run_applescript(script):
    """Run an AppleScript command via osascript (reliable for system-level actions)."""
    subprocess.Popen(
        ["osascript", "-e", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def gesture_mission_control():
    """Trigger Mission Control."""
    run_applescript(
        'tell application "System Events" to key code 126 using control down'
    )
    print("[gesture] Mission Control")


def gesture_app_expose():
    """Trigger App Exposé."""
    run_applescript(
        'tell application "System Events" to key code 125 using control down'
    )
    print("[gesture] App Exposé")


def gesture_space_left():
    """Switch to left desktop space."""
    run_applescript(
        'tell application "System Events" to key code 123 using control down'
    )
    print("[gesture] Space Left")


def gesture_space_right():
    """Switch to right desktop space."""
    run_applescript(
        'tell application "System Events" to key code 124 using control down'
    )
    print("[gesture] Space Right")


def gesture_launchpad():
    """Open Launchpad."""
    subprocess.Popen(
        ["open", "-a", "Launchpad"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("[gesture] Launchpad")


def gesture_show_desktop():
    """Show Desktop via AppleScript."""
    run_applescript(
        'tell application "System Events" to key code 103 using {command down, fn down}'
    )
    print("[gesture] Show Desktop")


async def handle_ws(websocket):
    """Handle a single WebSocket connection from a phone."""
    global sensitivity, scroll_speed
    print("[ws] Client connected")
    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            action = msg.get("action")
            if action == "move":
                move_mouse(msg.get("dx", 0), msg.get("dy", 0))
            elif action == "click":
                click()
            elif action == "rightclick":
                right_click()
            elif action == "scroll":
                scroll(msg.get("dx", 0), msg.get("dy", 0))
            elif action == "sensitivity":
                sensitivity = float(msg.get("value", 2.0))
                print(f"[ws] Sensitivity set to {sensitivity}")
            elif action == "scrollspeed":
                scroll_speed = float(msg.get("value", 1.0))
                print(f"[ws] Scroll speed set to {scroll_speed}")
            # Multi-finger gestures
            elif action == "mission_control":
                gesture_mission_control()
            elif action == "app_expose":
                gesture_app_expose()
            elif action == "space_left":
                gesture_space_left()
            elif action == "space_right":
                gesture_space_right()
            elif action == "launchpad":
                gesture_launchpad()
            elif action == "show_desktop":
                gesture_show_desktop()
    except websockets.exceptions.ConnectionClosed:
        pass
    print("[ws] Client disconnected")


def start_http_server():
    """Serve index.html from the script's directory on HTTP_PORT."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *_: None  # suppress noisy logs

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", HTTP_PORT), handler) as httpd:
        httpd.serve_forever()


def generate_qr_string(text):
    """Generate a scannable QR code string for the terminal.
    Uses qrcode library's proven ASCII renderer (inverted for dark terminals)."""
    try:
        import io
        import qrcode
    except ImportError:
        return None

    qr = qrcode.QRCode(
        box_size=1, border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
    )
    qr.add_data(text)
    qr.make(fit=True)

    # Capture the built-in print_ascii output (uses half-blocks, always scannable)
    buf = io.StringIO()
    qr.print_ascii(out=buf, invert=True)
    raw = buf.getvalue()

    # Indent each line for nice display
    return "\n".join("   " + line for line in raw.splitlines())


def print_qr_fallback(url):
    """Print a simple text-art QR placeholder if no QR library is available."""
    print(f"\n   Scan this URL on your phone:")
    print(f"   \033[1;4m{url}\033[0m")
    print(f"\n   (Install 'qrcode' for a scannable QR in terminal:")
    print(f"    pip install qrcode)")


async def main():
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{HTTP_PORT}"

    # Start HTTP server in a daemon thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    print()
    print("=" * 52)
    print("   FingerFly")
    print("=" * 52)
    print()

    # Show QR code in terminal
    qr_str = generate_qr_string(url)
    if qr_str:
        print("   Scan with your phone camera:")
        print()
        print(qr_str)
        print()
    else:
        print_qr_fallback(url)
        print()

    print(f"   \033[1mhttp://{local_ip}:{HTTP_PORT}\033[0m")
    print()
    print(f"   HTTP  -> 0.0.0.0:{HTTP_PORT}")
    print(f"   WS    -> 0.0.0.0:{WS_PORT}")
    print()
    print("   Make sure Accessibility is enabled:")
    print("   System Settings > Privacy & Security")
    print("   > Accessibility > enable Terminal")
    print()
    print("=" * 52)
    print("   Press Ctrl+C to stop")
    print("=" * 52)
    print()

    async with websockets.serve(handle_ws, "0.0.0.0", WS_PORT):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down.")
