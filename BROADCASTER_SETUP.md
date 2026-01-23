# 🎬 Broadcaster Agent Quick Setup

Run this on your **local Windows/Mac/Linux computer** (NOT on the Render server).

## Step 1: Get Session Credentials

On your browser:
1. Go to: https://jvps.onrender.com
2. Click **"Start Broadcasting"**
3. Enter your name and room name
4. Copy the **Session ID** and **Password**

## Step 2: Run the Broadcaster Agent

Open terminal on your local computer:

```bash
cd path/to/BROADCAST
python agent/broadcaster_agent.py
```

## Step 3: Enter Credentials

When prompted:
```
  Session ID (SESSION-XXXXXX): [PASTE_YOUR_SESSION_ID]
  Password (XXXXXXXX): [PASTE_YOUR_PASSWORD]
```

## Step 4: Wait for Connection

You should see:
```
[14:32:01] 🔌 Connecting to https://jvps.onrender.com...
[14:32:02] ✅ Connected to Render server
[14:32:03] ✅ Broadcaster registered!

✅ BROADCASTER AGENT IS RUNNING
📱 Your iPhone/Browser can now control this desktop!
⌨️  Waiting for control commands...
```

## Step 5: Test with iPhone/Browser

1. Go to the viewer link from your broadcast session
2. Your iPhone/browser can now:
   - Move your mouse
   - Click buttons
   - Type on your keyboard
   - Scroll windows

## Troubleshooting

### ❌ Connection failed?

Check:
- [ ] Internet connection working
- [ ] https://jvps.onrender.com is online
- [ ] Session ID is exactly correct
- [ ] Password is exactly correct

### ❌ Commands not executing?

- Check broadcaster agent is running (terminal should show messages)
- Check console for any errors
- Restart the broadcaster agent
- Verify controls are being sent (should see logs in terminal)

### ❌ Mouse not moving?

- Broadcaster agent must be actively running
- Make sure terminal window is visible (not minimized)
- Try a simple mouse move command first
- Check no firewall blocking outgoing connections

## Keyboard Shortcuts

While broadcaster agent is running:
- **Ctrl+C** - Stop the broadcaster agent
- **Esc** - PyAutoGUI failsafe (if enabled) - moves cursor to top-left corner

## Features

✅ **Mouse Control**
- Move cursor
- Click (left, right, middle)
- Drag
- Scroll

✅ **Keyboard Control**
- Press keys
- Type text
- Hotkeys (Ctrl+C, Ctrl+V, Alt+Tab, etc.)

## Technical Notes

- Broadcaster agent runs **locally on your computer**
- Render server only **relays commands** (doesn't execute them)
- All mouse/keyboard control is executed locally
- Your desktop screen is NOT shared to viewers (control only)
- Connection uses Socket.IO over WebSocket/polling

## Next Steps

1. Share the viewer link with your friends/colleagues
2. They can connect and control your desktop
3. Your machine executes all control commands

---

**Need help?** Check logs.txt on the Render server for detailed events.
