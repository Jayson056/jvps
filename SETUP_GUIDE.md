# OmniStream Pro - Setup & Usage Guide

## Architecture

The system has **two separate broadcaster components**:

1. **Browser-based Broadcaster** (`webrtc_broadcaster.js`) - Handles screen capture & WebRTC streaming
2. **Python Agent** (`screenshare.py`) - Handles remote keyboard & mouse control

Both must work together for full functionality.

---

## Control Flow for Remote Input

```
Viewer (Browser) 
    → sends control_input 
    → Flask Server (app.py) 
    → relays to Python Agent (screenshare.py) 
    → executes with pyautogui
```

---

## Critical Setup Step: Device ID Matching

**The Problem Fixed:**
- Browser creates a `broadcaster_id` when you click "New Broadcast"
- Python agent must use the **same** `broadcaster_id` to receive control signals
- Previously, the agent generated its own random ID, preventing control messages from reaching it

**The Solution:**
Pass the broadcaster_id from the web UI to the Python agent via command line argument.

---

## How to Use

### Step 1: Start the Flask Server
```powershell
python app.py
```
This starts the signaling server at `http://localhost:58247`

### Step 2: Open Browser and Create Broadcast
1. Go to `http://localhost:58247/`
2. Click **"New Broadcast"**
3. **Copy the Device ID** shown on the page (e.g., `a1b2c3d4-...`)

### Step 3: Start Python Agent with Device ID
In a new terminal, run:
```powershell
python agent\screenshare.py <BROADCASTER_ID>
```

Replace `<BROADCASTER_ID>` with the Device ID from Step 2.

**Example:**
```powershell
python agent\screenshare.py a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Step 4: Connect Viewer
1. On another machine/browser, go to `http://[broadcaster-ip]:58247/view_list`
2. Click the session you just created
3. **Allow notifications** and **screen sharing permissions** when prompted
4. Once connected, you should see the broadcaster's screen
5. **Test control:** Move your mouse or type on the viewer - it should control the broadcaster

---

## Troubleshooting

### Viewer can't see screen
- Check that browser-based broadcaster allowed screen capture
- Verify WebRTC connection in browser console

### Viewer can see screen but mouse/keyboard not working

**Check these in order:**

1. **Verify Python agent connected:**
   - Look for log: `[INFO] Connected to server at http://localhost:58247`
   - Look for log: `[INFO] Registered with device_id: ...`

2. **Verify device ID matches:**
   - Device ID from "New Broadcast" page must exactly match what you passed to `python agent\screenshare.py`

3. **Check Flask server logs for control relay:**
   - Should see: `[INFO] Relaying control input to broadcaster [device_id]`
   - If you see errors like `[ERROR] Broadcaster [id] not registered in devices`, then the device_id doesn't match

4. **Enable browser developer console:**
   - Viewer: Open DevTools → Console tab
   - Verify you see `[REMOTE CONTROL] Action received:` messages when you move the mouse

5. **Check Python agent logs:**
   - Should see: `[INFO] Control input received:` when viewer moves mouse
   - If not, control signal isn't reaching the agent

### Common Mistakes

❌ **Wrong:** Running agent without device ID
```powershell
python agent\screenshare.py  # ← Missing device ID!
```

✅ **Right:** Running agent with device ID from web UI
```powershell
python agent\screenshare.py a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

❌ **Wrong:** Using different device ID than shown in browser
- Browser shows: `Device ID: abc123`
- But you run: `python agent\screenshare.py xyz789`

✅ **Right:** Copy-paste the exact device ID

---

## Debug Mode

To see more details, add debug logging:

**In app.py**, the Flask server shows:
- When control signals are received
- Which broadcaster they're being relayed to
- Any errors in routing

**In screenshare.py**, the agent shows:
- Connection status
- Device ID being used
- Control inputs being executed

---

## Technical Details

### Socket.IO Device Registry

The server maintains two dictionaries:

```python
devices = {
    'device_id': {
        'role': 'broadcaster' | 'viewer',
        'sid': 'socketio_session_id'
    }
}

sessions = {
    'session_id': {
        'broadcaster': 'device_id',
        'viewers': ['device_id', ...]
    }
}
```

When control input arrives:
1. Viewer's session_id is used to look up broadcaster device_id
2. Broadcaster device_id is used to get Socket.IO SID
3. Signal is emitted to that specific SID with `to=` parameter

### Port Mappings

- **Flask + SocketIO Server:** `0.0.0.0:58247`
- **Python Agent connects to:** `http://localhost:58247`
- **Viewers connect to:** `http://[broadcaster-ip]:58247`

