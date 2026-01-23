#!/usr/bin/env python3
"""
JVPS Connection Tester
======================================
Tests if Broadcaster Agent can work properly

Run this BEFORE starting broadcaster_agent.py to verify setup
"""

import os
import sys
import time

RENDER_SERVER = os.environ.get('RENDER_SERVER', 'https://jvps.onrender.com')

print("\n" + "=" * 70)
print("🧪 JVPS Broadcaster Agent - Connection Tester")
print("=" * 70)
print(f"Server: {RENDER_SERVER}\n")

# Test 1: Render server reachable
print("📡 Test 1: Is Render server reachable?")
try:
    import requests
    response = requests.head(RENDER_SERVER, timeout=5)
    print(f"   ✅ Server is ONLINE (HTTP {response.status_code})")
    test1 = True
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    test1 = False

# Test 2: Socket.IO connection
print("\n🔌 Test 2: Can Socket.IO connect?")
try:
    import socketio
    sio = socketio.Client(reconnection=False)
    
    connected = False
    @sio.on('connect')
    def on_connect():
        global connected
        connected = True
    
    sio.connect(RENDER_SERVER, transports=['websocket', 'polling'], wait_timeout=5)
    time.sleep(1)
    sio.disconnect()
    
    if connected:
        print(f"   ✅ Socket.IO connection works")
        test2 = True
    else:
        print(f"   ❌ Connection failed to establish")
        test2 = False
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    test2 = False

# Test 3: PyAutoGUI installed and working
print("\n⌨️  Test 3: Is PyAutoGUI working?")
try:
    import pyautogui
    # Just get screen size - doesn't execute any control
    size = pyautogui.size()
    print(f"   ✅ PyAutoGUI working - Screen: {size[0]}x{size[1]}")
    test3 = True
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    test3 = False

# Test 4: Socket.IO library installed
print("\n📦 Test 4: Required packages installed?")
try:
    import socketio
    print(f"   ✅ python-socketio: {socketio.__version__ if hasattr(socketio, '__version__') else 'OK'}")
    test4 = True
except ImportError:
    print(f"   ❌ python-socketio not installed")
    test4 = False

# Summary
print("\n" + "=" * 70)
print("📊 Summary:")
print("=" * 70)
print(f"  Render server reachable:  {'✅' if test1 else '❌'}")
print(f"  Socket.IO connection:     {'✅' if test2 else '❌'}")
print(f"  PyAutoGUI working:        {'✅' if test3 else '❌'}")
print(f"  Required packages:        {'✅' if test4 else '❌'}")

if all([test1, test2, test3, test4]):
    print("\n✅ ALL TESTS PASSED - Ready to run broadcaster_agent.py!")
    print("\nRun: python broadcaster_agent.py")
else:
    print("\n⚠️  Some tests failed - fix issues before running broadcaster_agent.py")
    if not test1:
        print("\n   Fix: Check internet connection or Render server status")
    if not test2:
        print("\n   Fix: Check firewall settings, try VPN, or check Render status")
    if not test3:
        print("\n   Fix: Install PyAutoGUI: pip install pyautogui")
    if not test4:
        print("\n   Fix: Install packages: pip install -r requirements.txt")

print("=" * 70 + "\n")
