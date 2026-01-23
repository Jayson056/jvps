#!/usr/bin/env python3
"""
JVPS Broadcaster Agent - Simple Version
=========================================
Runs on the broadcaster's local machine.
Connects to Render relay server and receives control commands.
Executes mouse/keyboard control on the local desktop.

Usage:
  python broadcaster_agent.py
"""

import pyautogui
import socketio
import threading
import time
import os
from datetime import datetime

# Disable PyAutoGUI failsafe (optional - press Ctrl+C to stop instead)
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05  # Delay between commands

# Configuration
RENDER_SERVER = os.environ.get('RENDER_SERVER', 'https://jvps.onrender.com')
MOUSE_SPEED = 0.1  # Duration for mouse movement

# Socket.IO client
sio = socketio.Client(reconnection=True, reconnection_attempts=10, reconnection_delay=3)

# Global state
connected = False
broadcaster_registered = False
session_id = None
device_id = None

print("\n" + "=" * 70)
print("🎬 JVPS Broadcaster Agent")
print("=" * 70)
print(f"Server: {RENDER_SERVER}")
print("=" * 70 + "\n")

# ---------------------------
# Control Execution Functions
# ---------------------------

def execute_mouse_command(data):
    """Execute mouse control command"""
    try:
        action = data.get('action', 'move')
        x = data.get('x')
        y = data.get('y')
        button = data.get('button', 'left')
        
        if action == 'move' and x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=MOUSE_SPEED)
            print(f"  🖱️ MOUSE: Moved to ({x}, {y})")
            
        elif action == 'click' and x is not None and y is not None:
            pyautogui.click(x, y, button=button)
            print(f"  🖱️ MOUSE: Clicked {button} at ({x}, {y})")
            
        elif action == 'drag' and x is not None and y is not None:
            duration = data.get('duration', 0.3)
            pyautogui.drag(x, y, duration=duration, button=button)
            print(f"  🖱️ MOUSE: Dragged to ({x}, {y})")
            
        elif action == 'scroll':
            direction = data.get('direction', 'down')
            amount = data.get('amount', 3)
            if direction == 'up':
                pyautogui.scroll(amount)
                print(f"  🖱️ MOUSE: Scrolled UP")
            else:
                pyautogui.scroll(-amount)
                print(f"  🖱️ MOUSE: Scrolled DOWN")
                
    except Exception as e:
        print(f"  ❌ Mouse error: {e}")

def execute_keyboard_command(data):
    """Execute keyboard control command"""
    try:
        action = data.get('action', 'press')
        key = data.get('key', '').lower()
        
        if not key:
            return
        
        if action == 'press':
            pyautogui.press(key)
            print(f"  ⌨️  KEYBOARD: Pressed {key}")
            
        elif action == 'down':
            pyautogui.keyDown(key)
            print(f"  ⌨️  KEYBOARD: Key down {key}")
            
        elif action == 'up':
            pyautogui.keyUp(key)
            print(f"  ⌨️  KEYBOARD: Key up {key}")
            
        elif action == 'type':
            pyautogui.typewrite(key, interval=0.05)
            print(f"  ⌨️  KEYBOARD: Typed '{key}'")
            
        elif action == 'scroll':
            direction = data.get('direction', 'down')
            amount = data.get('amount', 3)
            if direction == 'up':
                pyautogui.scroll(amount)
            else:
                pyautogui.scroll(-amount)
            print(f"[MOUSE] Scrolled {direction}")
            
    except Exception as e:
        print(f"  ❌ Keyboard error: {e}")

# ---------------------------
# Socket.IO Event Handlers
# ---------------------------

@sio.on('connect')
def on_connect():
    global connected
    connected = True
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] ✅ Connected to Render server")

@sio.on('disconnect')
def on_disconnect():
    global connected, broadcaster_registered
    connected = False
    broadcaster_registered = False
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] ❌ Disconnected from server")

@sio.on('control_input')
def on_control_input(data):
    """Main event handler - receives control commands from Render"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] 📨 Control received:")
    
    control_type = data.get('type')
    control_data = data.get('data', {})
    
    if control_type == 'mouse':
        execute_mouse_command(control_data)
    elif control_type == 'keyboard':
        execute_keyboard_command(control_data)
    else:
        print(f"  ⚠️  Unknown control type: {control_type}")

@sio.on('error')
def on_error(data):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] ⚠️  Server error: {data}")

@sio.on('broadcaster_ready')
def on_broadcaster_ready(data):
    global broadcaster_registered
    broadcaster_registered = True
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] ✅ Broadcaster registered!")
    print(f"     Device ID: {data.get('device_id')}")
    print(f"     Session ID: {data.get('session_id')}")

# ---------------------------
# Connection Management
# ---------------------------

def connect_to_render(session_id_input, password_input):
    """Connect to Render relay server"""
    global session_id, device_id
    
    session_id = session_id_input
    device_id = session_id_input.replace('SESSION-', 'AGENT-')
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] 🔌 Connecting to {RENDER_SERVER}...")
    
    try:
        # Connect with custom auth
        sio.connect(
            RENDER_SERVER,
            auth={
                'session_id': session_id_input,
                'password': password_input,
                'role': 'broadcaster_agent'
            },
            transports=['websocket', 'polling'],
            wait_timeout=30
        )
        
        # Emit registration
        sio.emit('register_broadcaster_agent', {
            'session_id': session_id_input,
            'device_id': device_id,
            'timestamp': datetime.now().isoformat()
        })
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] ✅ Registration sent, waiting for confirmation...")
        
        return True
        
    except Exception as e:
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] ❌ Connection failed: {e}")
        print("\n     Troubleshooting:")
        print("     1. Check Render server is online: https://jvps.onrender.com")
        print("     2. Verify Session ID is correct")
        print("     3. Verify Password is correct")
        print("     4. Check your internet connection")
        return False

def keep_alive():
    """Send periodic keep-alive messages"""
    while True:
        try:
            if connected and broadcaster_registered:
                sio.emit('agent_heartbeat', {
                    'timestamp': datetime.now().isoformat()
                }, skip_sid=True)
            time.sleep(30)
        except Exception as e:
            pass

# ---------------------------
# Main
# ---------------------------

def main():
    """Main loop"""
    print("📝 Enter your Render session credentials:\n")
    
    session_id_input = input("  Session ID (SESSION-XXXXXX): ").strip()
    password_input = input("  Password (XXXXXXXX): ").strip()
    
    if not session_id_input or not password_input:
        print("\n❌ Session ID and password are required!")
        return 1
    
    print("\n" + "=" * 70)
    
    # Connect
    if not connect_to_render(session_id_input, password_input):
        return 1
    
    # Wait for connection
    for i in range(10):
        if connected:
            break
        time.sleep(1)
    
    if not connected:
        print("\n❌ Failed to connect")
        return 1
    
    # Start keep-alive thread
    heartbeat_thread = threading.Thread(target=keep_alive, daemon=True)
    heartbeat_thread.start()
    
    # Wait for registration
    for i in range(5):
        if broadcaster_registered:
            break
        time.sleep(1)
    
    if not broadcaster_registered:
        print("⚠️  Not registered yet, but will listen for commands...")
    
    print("\n" + "=" * 70)
    print("✅ BROADCASTER AGENT IS RUNNING")
    print("=" * 70)
    print("📱 Your iPhone/Browser can now control this desktop!")
    print("⌨️  Waiting for control commands...")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 70 + "\n")
    
    # Main loop
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        sio.disconnect()
        print("✅ Disconnected. Goodbye!")
        return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

if __name__ == '__main__':
    main()
