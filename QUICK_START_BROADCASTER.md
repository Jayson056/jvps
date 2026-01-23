# 🚀 JVPS Remote Desktop Control - Quick Start Guide

## Problem You're Experiencing

✅ Render server is relaying control commands (you see `[CONTROL_RELAY]` logs)  
❌ But mouse doesn't move on broadcaster machine (broadcaster agent not running)

**Solution**: You need to run the **Broadcaster Agent** on your local machine!

---

## ⚙️ Setup in 5 Steps

### Step 1: Get Session Credentials from Render

1. Visit https://jvps.onrender.com
2. Click **"Broadcast"** (or go to /brodcast_dets)
3. Enter device name (e.g., "My Desktop")
4. Click **"Create Session"**
5. You'll see:
   - **Device ID**: `DEV-XXXXXXXX`
   - **Session ID**: `SESSION-XXXXXXXX`
   - **Password**: `XXXXXXXX`

![Step 1](https://via.placeholder.com/600x300?text=Session+Created)

**Copy these three values - you'll need them next!**

---

### Step 2: Download and Install Broadcaster Agent

#### Option A: Using Python (Recommended for Windows/Mac/Linux)

```bash
# 1. Clone the repository (if you haven't already)
git clone https://github.com/Jayson056/jvps.git
cd jvps

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

#### Option B: Running Pre-built Binary (Coming Soon)

---

### Step 3: Run Broadcaster Agent

```bash
python agent/broadcaster_agent.py
```

You'll see this prompt:

```
======================================================================
JVPS Broadcaster Agent - Desktop Control
======================================================================
Server: https://jvps.onrender.com
======================================================================

📱 Enter Session ID (from Render): [PASTE SESSION ID HERE]
🔐 Enter Password (from Render): [PASTE PASSWORD HERE]
🏠 Enter Room Name (optional): My Desktop
```

**Paste the values from Step 1:**
- Session ID: `SESSION-XXXXXXXX`
- Password: `XXXXXXXX`
- Room Name: (optional, press Enter to use default)

---

### Step 4: Verify Agent is Connected

After pressing Enter, you should see:

```
======================================================================
✅ Broadcaster Agent is RUNNING
======================================================================
[INFO] Mouse and keyboard control is now ACTIVE
[INFO] iPhone/Browser can now control your desktop!
[INFO] Press Ctrl+C to stop
======================================================================
```

**Agent is now listening for control commands!** ✨

---

### Step 5: Control from iPhone/Browser

1. Visit https://jvps.onrender.com on any device (iPhone, iPad, laptop)
2. Click **"View Active Sessions"**
3. Select your session (you should see it listed)
4. Enter the password (same one from Step 1)
5. **Move your mouse - it should move on your desktop!** 🎉

---

## 🎮 Testing Control

### Test 1: Mouse Movement
- Move your finger/mouse on iPhone browser
- ✅ Desktop cursor should follow

### Test 2: Mouse Click
- Tap on the viewer screen
- ✅ Something should click on desktop

### Test 3: Keyboard
- Type in the input box on viewer
- ✅ Text should appear on desktop (app-dependent)

---

## 🔍 Troubleshooting

### Problem: "Connection refused" or "Cannot connect"

**Solution:**
```bash
# 1. Check Render server is online
curl https://jvps.onrender.com

# 2. Verify Session ID and Password are correct
# 3. Make sure Broadcaster Agent has internet connection
# 4. Check firewall isn't blocking connections
```

### Problem: Agent connects but no mouse movement

**Solution:**
```
✅ First verify:
- Is Render receiving commands? (Check Render logs for [CONTROL_RELAY])
- Is Agent connected? (Should see "RUNNING" message)
- Is Agent listening? (Should see @sio.on('control_input') events)

❌ If Agent not receiving:
1. Restart Agent: Press Ctrl+C, then run again
2. Check Session ID is exactly correct (copy-paste)
3. Verify password matches Render server
4. Try a fresh session
```

### Problem: Agent keeps disconnecting

**Solution:**
```bash
# 1. Check internet connection stability
# 2. Agent will auto-reconnect (up to 5 attempts)
# 3. If keeps failing, restart:

# Stop: Ctrl+C
# Restart: python agent/broadcaster_agent.py
```

---

## 📊 Architecture Flow

```
┌─────────────┐
│   iPhone    │ ← Viewer (Browser)
│  Camera     │   - Sees desktop video
│  Controls   │   - Sends mouse/keyboard input
└──────┬──────┘
       │ HTTPS WebSocket
       ▼
┌─────────────────────────────────┐
│  Render Relay Server (Cloud)    │
│  https://jvps.onrender.com      │
│  - Receives control from viewer │
│  - Relays to broadcaster        │
│  - No execution on server!      │
└──────┬──────────────────────────┘
       │ Socket.IO
       ▼
┌─────────────────────────────────┐
│   Your Desktop (Local)          │
│   broadcaster_agent.py running  │
│  - Receives control commands    │
│  - Executes mouse/keyboard      │
│  - Sends screen back to viewer  │
└─────────────────────────────────┘
```

---

## 📋 Logs to Check

### On Your Local Machine:

```bash
# Watch Broadcaster Agent logs
python agent/broadcaster_agent.py

# You should see:
[SOCKET.IO] Connected to Render server
[BROADCASTER] Registered - Device: DEV-XXXXX, Session: SESSION-XXXXX
[MOUSE] Moved to (1280, 720)
[MOUSE] Clicked left at (1280, 720)
```

### On Render Server:

Visit Render dashboard → jvps service → Logs tab

```
[CONTROL_RELAY] Relaying mouse control from viewer to broadcaster DEV-XXXXX
[SIGNAL_RELAY] Signal relayed from DEV-XXXXX to VIEWER-ID
```

---

## 🎯 Important Notes

1. **Broadcaster Agent must be running** on your local machine
2. **Render server is ONLY a relay** - it doesn't execute controls
3. **Agent listens on port 5000 by default** (no port forwarding needed)
4. **Works over internet** - viewers can be anywhere
5. **Encrypted connection** - HTTPS to Render, Socket.IO encrypted

---

## 🔐 Security Tips

1. **Unique Password**: Each session gets a random password
2. **Share Carefully**: Only share Session ID + Password with trusted people
3. **Session Timeout**: Sessions expire after inactivity (implement in v2)
4. **No Password Storage**: Passwords are not stored permanently
5. **HTTPS Only**: All communication is encrypted

---

## 📚 Next Steps

1. ✅ Download agent
2. ✅ Get session credentials
3. ✅ Run broadcaster agent
4. ✅ Test control from iPhone
5. 🎯 Share session with others
6. 📊 Monitor Render logs

---

## 💡 Pro Tips

### Multiple Sessions
```bash
# You can run multiple agent instances in different terminals
# Each with different session IDs
# This allows multiple broadcasters

# Terminal 1:
python agent/broadcaster_agent.py
# Session 1: SESSION-ABC123

# Terminal 2:
python agent/broadcaster_agent.py
# Session 2: SESSION-XYZ789
```

### Screen Resolution
Agent auto-detects your screen resolution. No configuration needed!

### Latency
For best experience:
- Use WiFi (not 3G/LTE if possible)
- Reduce screen resolution in viewer if needed
- Close unnecessary browser tabs

### Keeping Agent Running
Use a process manager for 24/7 operation:
- **Windows**: Task Scheduler
- **Mac**: LaunchAgent
- **Linux**: systemd or supervisor

---

## 📞 Support

**Issues or questions?**

1. Check Render logs: Dashboard → jvps service → Logs
2. Check Agent console output (where you ran the script)
3. Review DESKTOP_CONTROL_ARCHITECTURE.md
4. Check GitHub issues: github.com/Jayson056/jvps/issues

---

## ✅ Checklist

Before testing, verify:

- [ ] Render server is online (https://jvps.onrender.com)
- [ ] You have Session ID, Password, Room Name from Render
- [ ] Python 3.9+ is installed
- [ ] requirements.txt dependencies installed
- [ ] Broadcaster Agent is running (shows "✅ RUNNING" message)
- [ ] Internet connection is stable
- [ ] No firewall blocking connections
- [ ] iPhone/Browser can reach Render server

---

**You're all set! Enjoy remote desktop control! 🎉**
