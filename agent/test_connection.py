#!/usr/bin/env python3
"""
JVPS Connection Tester
Tests if Broadcaster Agent can connect to Render relay server
"""

import socketio
import os
import sys

RENDER_SERVER = os.environ.get('RENDER_SERVER', 'https://jvps.onrender.com')

def test_render_server_reachable():
    """Test if Render server is online"""
    print("\n📡 Test 1: Is Render server reachable?")
    print(f"   Trying to reach: {RENDER_SERVER}")
    
    try:
        import requests
        response = requests.head(RENDER_SERVER, timeout=5)
        print(f"   ✅ Server is ONLINE (HTTP {response.status_code})")
        return True
    except Exception as e:
        print(f"   ❌ Server is OFFLINE or unreachable: {e}")
        return False

def test_socket_io_connection():
    """Test if Socket.IO connection works"""
    print("\n🔌 Test 2: Can connect via Socket.IO?")
    
    sio = socketio.Client()
    
    @sio.on('connect')
    def on_connect():
        print(f"   ✅ Socket.IO connection SUCCESSFUL")
        sio.disconnect()
    
    @sio.on('error')
    def on_error(data):
        print(f"   ❌ Socket.IO error: {data}")
        sio.disconnect()
    
    try:
        print(f"   Attempting connection to {RENDER_SERVER}...")
        sio.connect(RENDER_SERVER, transports=['websocket', 'polling'], wait_timeout=10)
        return True
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def test_pyautogui_ready():
    """Test if PyAutoGUI is installed and can control mouse"""
    print("\n🖱️  Test 3: Is PyAutoGUI ready?")
    
    try:
        import pyautogui
        print(f"   ✅ PyAutoGUI is installed")
        print(f"   ✅ Mouse position: {pyautogui.position()}")
        print(f"   ✅ Screen resolution: {pyautogui.size()}")
        return True
    except Exception as e:
        print(f"   ❌ PyAutoGUI error: {e}")
        return False

def test_mss_ready():
    """Test if mss is installed and can capture screen"""
    print("\n📸 Test 4: Is screen capture ready?")
    
    try:
        import mss
        with mss.mss() as sct:
            monitors = sct.monitors
            print(f"   ✅ MSS is installed")
            print(f"   ✅ Monitors detected: {len(monitors) - 1}")
            for i, monitor in enumerate(monitors[1:], 1):
                print(f"      Monitor {i}: {monitor['width']}x{monitor['height']}")
        return True
    except Exception as e:
        print(f"   ❌ MSS error: {e}")
        return False

def main():
    print("=" * 70)
    print("JVPS Broadcaster Agent - Connection Tester")
    print("=" * 70)
    
    tests = [
        ("Render Server Reachable", test_render_server_reachable),
        ("Socket.IO Connection", test_socket_io_connection),
        ("PyAutoGUI Ready", test_pyautogui_ready),
        ("Screen Capture Ready", test_mss_ready),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All systems ready! You can now run:")
        print("   python agent/broadcaster_agent.py")
    else:
        print("\n❌ Fix issues above before running broadcaster agent")
    
    print("=" * 70 + "\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
