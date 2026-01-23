"""
JVPS Desktop Broadcaster Agent
================================
This is a LOCAL client that runs on the broadcaster's machine.
It handles:
1. Desktop screen capture
2. Mouse and keyboard control
3. WebRTC peer connection
4. Communication with the Render relay server

This runs on the broadcaster's computer (Windows/Mac/Linux), NOT on Render.
The Render server only handles signaling relay.
"""

import pyautogui
import mss
import numpy as np
import io
from PIL import Image
import socketio
import asyncio
import threading
import json
import os
from datetime import datetime

# Initialize Socket.IO client
sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=2)

# Configuration
RENDER_SERVER = os.environ.get('RENDER_SERVER', 'https://jvps.onrender.com')
SESSION_ID = None
DEVICE_ID = None
PASSWORD = None

# Desktop capture
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 30
MOUSE_SPEED = 0.1

# PyAutoGUI configuration
pyautogui.FAILSAFE = True  # Press ESC in top-left corner to stop
pyautogui.PAUSE = 0.01  # Minimum delay between commands

print("=" * 70)
print("JVPS Desktop Broadcaster Agent")
print("=" * 70)
print(f"Server: {RENDER_SERVER}")
print(f"Python: {__name__}")
print("=" * 70)

# ---------------------------
# Screen Capture Functions
# ---------------------------
def capture_screen():
    """Capture the current screen"""
    try:
        with mss.mss() as sct:
            # Capture primary monitor
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            
            # Convert to PIL Image
            img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
            
            # Encode to JPEG for WebRTC
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=80)
            buffer.seek(0)
            
            return buffer.getvalue()
    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None

# ---------------------------
# Desktop Control Functions
# ---------------------------
def execute_mouse_control(data):
    """Execute mouse control command"""
    try:
        x = data.get('x')
        y = data.get('y')
        button = data.get('button', 'left')
        action = data.get('action', 'move')  # move, click, drag
        
        if action == 'move' and x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=MOUSE_SPEED)
            print(f"[MOUSE] Moved to ({x}, {y})")
            
        elif action == 'click' and x is not None and y is not None:
            pyautogui.click(x, y, button=button)
            print(f"[MOUSE] Clicked {button} at ({x}, {y})")
            
        elif action == 'drag' and x is not None and y is not None:
            duration = data.get('duration', 0.5)
            pyautogui.drag(x, y, duration=duration, button=button)
            print(f"[MOUSE] Dragged {button} to ({x}, {y})")
            
        elif action == 'scroll':
            direction = data.get('direction', 'down')
            amount = data.get('amount', 3)
            if direction == 'up':
                pyautogui.scroll(amount)
            else:
                pyautogui.scroll(-amount)
            print(f"[MOUSE] Scrolled {direction}")
            
    except Exception as e:
        print(f"[ERROR] Mouse control failed: {e}")

def execute_keyboard_control(data):
    """Execute keyboard control command"""
    try:
        key = data.get('key', '').lower()
        action = data.get('action', 'press')  # press, down, up, type
        
        if action == 'type' and key:
            pyautogui.typewrite(key, interval=0.05)
            print(f"[KEYBOARD] Typed: {key}")
            
        elif action == 'press' and key:
            pyautogui.press(key)
            print(f"[KEYBOARD] Pressed: {key}")
            
        elif action == 'down' and key:
            pyautogui.keyDown(key)
            print(f"[KEYBOARD] Key down: {key}")
            
        elif action == 'up' and key:
            pyautogui.keyUp(key)
            print(f"[KEYBOARD] Key up: {key}")
            
        elif action == 'hotkey':
            # Example: 'ctrl+c', 'cmd+v', 'alt+tab'
            keys = key.split('+')
            pyautogui.hotkey(*keys)
            print(f"[KEYBOARD] Hotkey: {key}")
            
    except Exception as e:
        print(f"[ERROR] Keyboard control failed: {e}")

# ---------------------------
# Socket.IO Event Handlers
# ---------------------------
@sio.on('connect')
def on_connect():
    print("[SOCKET.IO] Connected to Render server")

@sio.on('disconnect')
def on_disconnect():
    print("[SOCKET.IO] Disconnected from server")

@sio.on('broadcaster_registered')
def on_broadcaster_registered(data):
    """Confirmation that broadcaster was registered on server"""
    global DEVICE_ID, SESSION_ID
    DEVICE_ID = data.get('device_id')
    SESSION_ID = data.get('session_id')
    print(f"[BROADCASTER] Registered - Device: {DEVICE_ID}, Session: {SESSION_ID}")

@sio.on('control_input')
def on_control_input(data):
    """Receive control input from viewer via relay server"""
    control_type = data.get('type')
    control_data = data.get('data', {})
    
    if control_type == 'mouse':
        execute_mouse_control(control_data)
    elif control_type == 'keyboard':
        execute_keyboard_control(control_data)
    else:
        print(f"[WARNING] Unknown control type: {control_type}")

@sio.on('signal_from_viewer')
def on_signal_from_viewer(data):
    """Relay WebRTC signal from viewer"""
    print(f"[WEBRTC] Signal from viewer: {data.get('type', 'unknown')}")
    # In full implementation, would process WebRTC signals here

# ---------------------------
# Connection Management
# ---------------------------
def connect_to_server(session_id, password, room_name):
    """Connect to Render relay server"""
    global SESSION_ID
    SESSION_ID = session_id
    
    try:
        print(f"\n[CONNECTING] To: {RENDER_SERVER}")
        print(f"[SESSION] ID: {session_id}")
        print(f"[ROOM] Name: {room_name}")
        
        # Connect with authentication
        sio.connect(
            RENDER_SERVER,
            auth={'session_id': session_id, 'password': password, 'role': 'broadcaster'},
            transports=['websocket', 'polling']
        )
        
        # Register as broadcaster
        sio.emit('register_broadcaster', {
            'session_id': session_id,
            'room_name': room_name,
            'device_id': str(uuid.uuid4())
        })
        
        print("[STATUS] Broadcaster agent running")
        print("[CONTROLS] Mouse and keyboard ready for control")
        print("[INFO] Press Esc (top-left corner) to stop PyAutoGUI")
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False
    
    return True

def send_heartbeat():
    """Send periodic heartbeat to keep connection alive"""
    while True:
        try:
            if sio.connected:
                sio.emit('heartbeat', {'timestamp': datetime.now().isoformat()})
            asyncio.sleep(30)
        except Exception as e:
            print(f"[ERROR] Heartbeat failed: {e}")

# ---------------------------
# Main
# ---------------------------
def main():
    """Main broadcaster agent loop"""
    print("\n" + "=" * 70)
    print("JVPS Broadcaster Agent - Configuration")
    print("=" * 70)
    
    # Get session details
    session_id = input("Enter Session ID: ").strip()
    password = input("Enter Password: ").strip()
    room_name = input("Enter Room Name (optional): ").strip() or "Shared Screen"
    
    if not session_id or not password:
        print("[ERROR] Session ID and password are required")
        return
    
    # Connect to Render relay server
    if not connect_to_server(session_id, password, room_name):
        print("[ERROR] Failed to connect to relay server")
        return
    
    # Start heartbeat thread
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()
    
    # Keep the agent running
    try:
        print("\n[INFO] Agent is running. Press Ctrl+C to stop.")
        while sio.connected:
            asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down broadcaster agent...")
        sio.disconnect()
        print("[INFO] Disconnected. Goodbye!")

if __name__ == '__main__':
    import uuid
    import asyncio
    
    main()
