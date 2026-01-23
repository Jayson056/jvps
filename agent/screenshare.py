# agent/screenshare.py
import socketio
import pyautogui
import threading
import time
import uuid
import platform
import sys

# ---------------------------
# CONFIGURATION
# ---------------------------
# Replace with your Flask server URL (e.g., http://192.168.1.5:58247)
SERVER_URL = "http://localhost:58247" 
ROLE = "broadcaster"
RECONNECT_DELAY = 5  # seconds

# Disable PyAutoGUI fail-safe if you want the mouse to move to corners 
# (Caution: keep it True if you want to be able to stop the script by slamming the mouse to a corner)
pyautogui.FAILSAFE = True

# ---------------------------
# GLOBALS
# ---------------------------
# Get device_id from command line argument (passed by the web UI)
# Usage: python screenshare.py <broadcaster_id>
device_id = sys.argv[1] if len(sys.argv) > 1 else str(uuid.uuid4())
sio = socketio.Client()
approved_viewers = set()

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def execute_control(action):
    """
    Executes incoming control commands from the remote viewer.
    action: dict with keys:
        - type: 'mouse' or 'keyboard'
        - data: dict containing coordinates or key names
    """
    try:
        if action['type'] == 'mouse':
            data = action['data']
            x, y = data.get('x'), data.get('y')
            
            if x is not None and y is not None:
                # Handle Movement
                if data.get('move'):
                    # _pause=False makes the movement near-instant
                    pyautogui.moveTo(x, y, _pause=False)
                
                # Handle Clicks
                if data.get('click'):
                    button = data.get('button', 'left')
                    pyautogui.click(x, y, button=button)

        elif action['type'] == 'keyboard':
            data = action['data']
            key = data.get('key')
            action_type = data.get('action', 'press')

            # Standardize key names (browsers often send capitalized names)
            key = key.lower() if len(key) > 1 else key

            if action_type == 'press':
                pyautogui.press(key)
            elif action_type == 'down':
                pyautogui.keyDown(key)
            elif action_type == 'up':
                pyautogui.keyUp(key)

    except Exception as e:
        print(f"[ERROR] Failed to execute control: {e}")

def keep_alive():
    """
    Background thread to send heartbeats to the server to prevent timeouts.
    """
    while True:
        if sio.connected:
            try:
                sio.emit('heartbeat', {'device_id': device_id})
            except:
                pass
        time.sleep(10)

# ---------------------------
# SOCKET.IO EVENT HANDLERS
# ---------------------------
@sio.event
def connect():
    print(f"[INFO] Connected to server at {SERVER_URL}")
    # Register the agent with the server using our device_id
    print(f"[INFO] Registering device with ID: {device_id}")
    sio.emit('register_device', {'role': ROLE, 'device_id': device_id})
    
@sio.on('device_registered')
def on_registered(data):
    global device_id
    device_id = data['device_id']
    print(f"[INFO] Registered with device_id: {device_id}")

@sio.on('control_input')
def on_control_input(data):
    """
    Triggered whenever the server relays a control event from a viewer.
    """
    print(f"[INFO] Control input received: {data}")
    execute_control(data)

@sio.on('viewer_request')
def on_viewer_request(data):
    """
    Handle requests from viewers wanting to join the session.
    Automatically approves for now.
    """
    viewer_id = data['viewer_id']
    print(f"[INFO] Viewer requesting access: {viewer_id}")
    
    approved_viewers.add(viewer_id)
    sio.emit('approve_viewer', {
        'viewer_id': viewer_id, 
        'approved': True
    })

@sio.event
def disconnect():
    print("[WARNING] Disconnected from server. Reconnect logic will trigger...")

# ---------------------------
# CONNECTION LOGIC
# ---------------------------
def connect_to_server():
    """
    Persistent connection loop that retries until a connection is established.
    """
    while not sio.connected:
        try:
            sio.connect(SERVER_URL, wait_timeout=10)
            break
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}. Retrying in {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)

# ---------------------------
# MAIN EXECUTION
# ---------------------------
if __name__ == '__main__':
    print(f"[INFO] Starting Broadcaster Agent on {platform.system()}")
    print(f"[INFO] Device ID: {device_id}")
    print(f"[INFO] Server URL: {SERVER_URL}")
    print(f"[INFO] Local Screen Resolution: {pyautogui.size()}")

    # 1. Start heartbeat thread
    threading.Thread(target=keep_alive, daemon=True).start()

    # 2. Establish connection to Flask-SocketIO server
    connect_to_server()

    # 3. Main loop to keep the process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[INFO] Exiting agent...")
        sio.disconnect()
        sys.exit(0)