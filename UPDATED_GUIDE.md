# OmniStream Pro v2 — Integrated & Auto-Connect Guide

## 🎉 What's New

✅ **PyAutoGUI integrated into Flask** — No separate agent needed
✅ **Auto-connect for viewers** — Share one link for instant access  
✅ **Direct control execution** — Mouse/keyboard work immediately
✅ **Enhanced UI** — Status indicators, latency tracking, auto-viewer link
✅ **Simplified setup** — Just run the Flask server

---

## 🚀 Quick Start

### 1. Start the Server (Only One Command!)

```powershell
cd C:\Users\USER\Documents\NewProject\BROADCAST
python app.py
```

The server will start on `http://localhost:58247`

### 2. Create a New Broadcast

Open your browser to:
```
http://localhost:58247/
```

Click **"📺 Start Broadcasting"**

You'll see:
- Your broadcaster screen preview
- **Device ID / Session ID** 
- **Auto-Viewer Link** to share with others (e.g., `http://localhost:58247/auto_viewer/[session-id]`)
- Real-time list of active viewers

### 3. Share Control Link

On the broadcaster page, you'll see the auto-viewer link in a box. Click **"📋 Copy Auto-Viewer Link"** to copy it.

**Share this link with anyone who needs to control your screen.**

### 4. Viewer Connects

The viewer clicks the link or goes to:
```
http://localhost:58247/auto_viewer/[session-id]
```

They will **automatically**:
- ✓ Register as a viewer
- ✓ Get approved for control
- ✓ See your screen
- ✓ Be able to move the mouse and type

---

## 🎮 How to Use (Viewer Side)

Once connected to the auto-viewer page:

| Action | How |
|--------|-----|
| **Move Mouse** | Move your cursor over the video |
| **Click** | Click on the video (left-click) |
| **Type** | Type on your keyboard |
| **Disable Controls** | Use "🖱️ Mouse: ON/OFF" or "⌨️ Kbd: ON/OFF" buttons |
| **Fullscreen** | Click "🖥️ Fullscreen" button |
| **Rotate View** | Click "🔄 Rotate" button |
| **Watch Latency** | Check the latency display (e.g., "Latency: 45ms") |

---

## 📋 System Architecture

### Before (v1)
```
Browser Broadcaster 
    → Screen Capture (WebRTC)
    → Viewer sees video
    → Viewer sends control input
    → Flask server receives
    → ❌ Needs separate Python agent to execute
```

### After (v2) — Integrated
```
Browser Broadcaster 
    → Screen Capture (WebRTC)
    → Viewer sees video via WebRTC P2P
    → Viewer sends control input
    → Flask server receives
    → ✅ Executes immediately via PyAutoGUI
```

---

## 🔗 URL Routes

| Route | Purpose |
|-------|---------|
| `/` | Home page with quick start buttons |
| `/broadcast/new` | Start a new broadcast session |
| `/view_list` | Browse all active broadcasts |
| `/view/<session_id>` | Manual viewer control (requires approval) |
| `/auto_viewer/<session_id>` | **Auto-connect viewer (instant approval)** |

---

## 🛠️ Configuration

Edit the following in `app.py` to customize:

```python
MOUSE_SPEED = 0.1  # seconds for mouse movement animation (lower = faster)
pyautogui.FAILSAFE = True  # Set to False to disable fail-safe (mouse to corner)
```

---

## 🐛 Troubleshooting

### Mouse/Keyboard Not Working?

1. **Check server is running:**
   ```powershell
   python app.py
   ```

2. **Check PyAutoGUI is installed:**
   ```powershell
   pip install pyautogui
   ```

3. **Check viewer sees the screen:**
   - Open browser console (F12)
   - Look for `[INFO] Remote stream received`
   - If you see errors, the WebRTC connection failed

4. **Check control inputs are received:**
   - Look in Flask server logs for:
   ```
   [INFO] Relaying control input to broadcaster
   ```
   - If you don't see this, viewer didn't send the input

### Viewer Can't See Screen?

1. **Check broadcaster allowed screen capture**
   - Browser should show a dialog asking for permission
   - Click "Allow" to share screen

2. **Check WebRTC connection:**
   - Browser console should show `[INFO] WebRTC State: connected`
   - If shows `failed`, check network connectivity

### Controls Disabled?

If the "Mouse: OFF" or "Kbd: OFF" buttons show:
- Controls are intentionally disabled
- Click the button to enable them again
- This is a safety feature to prevent accidental input

---

## 📊 Latency & Performance

The status bar shows:
- **Status Indicator:** Green dot = Connected
- **Latency:** Average roundtrip time to server

Target latencies:
- Local network: **10-30ms** ✓
- Same building: **30-100ms** ✓
- Internet: **100-300ms** ⚠️ (acceptable)
- Internet: **>300ms** ❌ (laggy)

To improve latency:
1. Use wired Ethernet instead of WiFi
2. Reduce screen resolution (if broadcaster can)
3. Reduce broadcast frame rate
4. Ensure low network congestion

---

## 🔐 Security Notes

⚠️ **WARNING:** This app allows **full remote control** of the machine running the broadcaster.

1. **Only share the auto-viewer link with trusted people**
2. **Session IDs are not secret** — Anyone with the URL can connect
3. **No authentication** — Add authentication layer before production use
4. **PyAutoGUI has full OS access** — Control what viewers can do

For production use, consider:
- Adding user authentication
- Rate limiting control inputs
- IP whitelisting
- Running in a restricted virtual machine

---

## 🎓 Technical Details

### Control Input Flow (v2)

```
Viewer (Browser)
    ↓ sends: { type: 'mouse', data: { x: 100, y: 200, move: true } }
Flask SocketIO Server (app.py)
    ↓ execute_control() function
PyAutoGUI on Server Machine
    ↓ pyautogui.moveTo(100, 200)
OS Level
    ↓ Mouse cursor moves
Server Machine Screen
    ↓ Displayed back to viewer via WebRTC
```

### Mouse Coordinate Scaling

Coordinates are scaled from viewer screen → broadcaster screen resolution:

```javascript
const x = (e.clientX - rect.left) * (remoteVideo.videoWidth / rect.width)
const y = (e.clientY - rect.top) * (remoteVideo.videoHeight / rect.height)
```

This ensures clicks are accurate regardless of zoom level.

---

## 📦 Dependencies

All installed via `requirements.txt`:
- **Flask** — Web framework
- **Flask-SocketIO** — Real-time communication
- **eventlet** — Async server
- **pyautogui** — OS-level control
- **python-socketio[client]** — Client library (for future agent)
- **Pillow** — Image processing (optional)

Install with:
```powershell
pip install -r requirements.txt
```

---

## 🎯 Next Steps / Future Features

- [ ] Authentication & user accounts
- [ ] Session recording
- [ ] File transfer
- [ ] Multi-viewer support with different permission levels
- [ ] Hardware acceleration for video encoding
- [ ] Mobile app support
- [ ] Docker containerization
- [ ] Cloud deployment guide

---

## 💬 Support

For issues:
1. Check browser console (F12) for error messages
2. Check Flask server console for errors
3. Enable debug logging in app.py
4. Test with localhost first before network testing

