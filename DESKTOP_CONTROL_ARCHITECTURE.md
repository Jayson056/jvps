# JVPS Desktop Control Architecture

## Problem with Current Implementation

❌ **Why Desktop Control Fails on Render**
- Render is a **headless server** (no X11 DISPLAY environment)
- PyAutoGUI requires graphical environment
- Attempting to execute `mouse.moveTo()` on server = error
- **This is correct behavior** - servers shouldn't control desktops!

## ✅ Proper Solution: Client-Side Desktop Control

The correct architecture separates concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    VIEWER (Browser)                         │
│  - Displays video stream                                    │
│  - Sends control inputs (mouse/keyboard)                    │
│  - WebRTC peer connection                                   │
└────────────────────┬────────────────────────────────────────┘
                     │ WebRTC Signals + Control Data
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            RENDER RELAY SERVER (Headless)                   │
│  - Relays WebRTC signaling only                             │
│  - Forwards control inputs to broadcaster                   │
│  - NO execution of controls                                 │
│  - Just a message relay/hub                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ Control Commands
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          BROADCASTER AGENT (Local Machine)                  │
│  - Runs on broadcaster's Windows/Mac/Linux                  │
│  - Executes mouse/keyboard controls locally                 │
│  - Captures screen via mss                                  │
│  - Sends stream to Render (via WebRTC)                      │
│  - Receives control commands from Render                    │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Components

### 1. **Render Server (Headless - Cloud)**
   - **Purpose**: Central relay hub
   - **Does**: 
     - Relays WebRTC signals
     - Forwards control commands
     - Manages sessions and authentication
     - Serves viewer web interface
   - **Does NOT**: Execute any desktop controls
   - **Technology**: Flask + Flask-SocketIO
   - **Location**: https://jvps.onrender.com

### 2. **Broadcaster Agent (Local - Desktop)**
   - **Purpose**: Captures screen and accepts controls
   - **Does**:
     - Connects to Render server
     - Captures desktop screen (mss)
     - Executes mouse/keyboard control (pyautogui)
     - Sends screen stream to viewer (WebRTC)
     - Listens for control commands from Render
   - **Technology**: Python + pyautogui + mss + socketio
   - **Location**: Broadcaster's computer
   - **Runs**: Standalone Python script (broadcaster_agent.py)

### 3. **Viewer (Browser - Any Client)**
   - **Purpose**: Remote control interface
   - **Does**:
     - Displays live video stream
     - Sends mouse/keyboard inputs
     - Verifies session password
     - Displays broadcaster screen
   - **Technology**: Browser + WebRTC + HTML/CSS/JS
   - **Location**: Any device with internet
   - **Access**: https://jvps.onrender.com

## Data Flow

### Initial Connection
```
1. Broadcaster Agent starts locally
2. Connects to Render server with session ID + password
3. Render server confirms registration
4. Broadcaster waits for viewer connections
```

### Control Flow
```
1. Viewer clicks/types on webpage
2. Browser sends control input to Render
3. Render server receives control command
4. Render forwards to Broadcaster Agent via Socket.IO
5. Broadcaster Agent executes on local machine:
   - pyautogui.moveTo(x, y)  ← Mouse moves
   - pyautogui.click()        ← Click happens
   - pyautogui.press(key)     ← Keyboard input
6. Broadcaster confirms execution (optional)
```

### Screen Capture Flow
```
1. Broadcaster Agent captures screen (every ~33ms for 30 FPS)
2. Compresses to JPEG (quality 80%)
3. Sends frame via WebRTC to viewer
4. Viewer browser displays in video element
```

## Installation & Usage

### On Broadcaster's Machine

```bash
# 1. Clone repository
git clone https://github.com/Jayson056/jvps.git
cd jvps

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run broadcaster agent
python agent/broadcaster_agent.py

# 5. Follow prompts:
#    - Enter Session ID (from Render server)
#    - Enter Password (from Render server)
#    - Enter Room Name (optional)
```

### On Viewer's Browser

```
1. Visit https://jvps.onrender.com
2. Click "View Active Sessions"
3. Select broadcaster from list
4. Enter password
5. Click controls or move mouse to control remote desktop
```

## Control Command Format

### Mouse Control
```json
{
  "type": "mouse",
  "data": {
    "action": "move",
    "x": 1280,
    "y": 720
  }
}
```

### Keyboard Control
```json
{
  "type": "keyboard",
  "data": {
    "action": "press",
    "key": "enter"
  }
}
```

### Supported Actions

| Type | Action | Parameters | Example |
|------|--------|------------|---------|
| mouse | move | x, y | `{x: 100, y: 200}` |
| mouse | click | x, y, button | `{x: 100, y: 200, button: 'left'}` |
| mouse | drag | x, y, duration, button | `{x: 100, y: 200}` |
| mouse | scroll | direction, amount | `{direction: 'down', amount: 3}` |
| keyboard | press | key | `{key: 'enter'}` |
| keyboard | type | text | `{text: 'hello'}` |
| keyboard | hotkey | keys | `{keys: ['ctrl', 'c']}` |

## Benefits of This Architecture

✅ **Headless Server Works** - No DISPLAY needed on Render  
✅ **Local Control Execution** - PyAutoGUI works on broadcaster's machine  
✅ **Scalable** - Single server can handle many broadcasters  
✅ **Secure** - Controls never leave broadcaster's network  
✅ **Cross-Platform** - Works on Windows, Mac, Linux  
✅ **No Installation** - Viewers only need browser  
✅ **Low Latency** - Direct WebRTC connection  

## Implementation Checklist

- [x] Render server (Flask + SocketIO)
- [x] Broadcaster Agent template (broadcaster_agent.py)
- [x] Socket.IO relay mechanism
- [x] Control command forwarding
- [x] Screen capture support
- [ ] Full WebRTC integration
- [ ] Screen sharing optimization
- [ ] Latency reduction
- [ ] Error handling & reconnection
- [ ] Compression & optimization

## Next Steps

1. **Complete Broadcaster Agent**
   - Add WebRTC screen stream
   - Add heartbeat/keep-alive
   - Add error recovery

2. **Update Render Server**
   - Verify control relay routes
   - Add control command validation
   - Optimize Socket.IO events

3. **Test Locally**
   - Run broadcaster_agent.py on local machine
   - Connect viewer through https://jvps.onrender.com
   - Test mouse and keyboard control

4. **Deploy & Monitor**
   - Push to GitHub
   - Render auto-deploys
   - Monitor logs for errors

## Troubleshooting

### Broadcaster Agent Won't Connect
```
- Check Session ID and Password are correct
- Verify Render server is running: https://jvps.onrender.com
- Check firewall/network allows WebSocket connections
```

### Controls Not Working
```
- Verify control command format in Socket.IO event
- Check broadcaster_agent.py is listening for 'control_input' event
- Review Render server logs for relay errors
```

### Screen Not Displaying
```
- Verify mss library is installed: pip install mss
- Check screen capture resolution matches display
- Review WebRTC connection in browser console
```

## References

- [PyAutoGUI Docs](https://pyautogui.readthedocs.io/)
- [mss Documentation](https://python-mss.readthedocs.io/)
- [Socket.IO Documentation](https://python-socketio.readthedocs.io/)
- [Render Deployment](https://render.com/docs)
- [WebRTC Protocol](https://webrtc.org/)
