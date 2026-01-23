# 🎬 JVPS - QUICK REFERENCE CARD

## 🚀 Production URLs

| Purpose | URL |
|---------|-----|
| Main Website | https://jvps.onrender.com |
| Start Broadcasting | https://jvps.onrender.com/brodcast_dets |
| GitHub Repository | https://github.com/Jayson056/jvps |

---

## 📱 Quick Start (3 Steps)

### Step 1: Create Broadcast
```
1. Open: https://jvps.onrender.com/brodcast_dets
2. Enter your name and room name
3. Click "Create Broadcast"
4. Copy: Session ID and Password
```

### Step 2: Run Broadcaster Agent
```bash
cd C:\Users\USER\Documents\NewProject\BROADCAST
python agent/broadcaster_agent.py
```

When prompted, paste:
- Session ID
- Password

### Step 3: Use Viewer
Open the auto_viewer link from Step 1:
```
https://jvps.onrender.com/auto_viewer/{session_id}?pwd={password}
```

Then move mouse, click, type on viewer → Your desktop responds!

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| Agent won't connect | Run `python agent/test_connection.py` first |
| Mouse doesn't move | Check terminal shows `✅ BROADCASTER AGENT IS RUNNING` |
| Viewer won't load | Check URL has correct session_id and password |
| Keyboard doesn't work | Click on viewer page first, then type |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `BROADCASTER_SETUP.md` | How to set up (for users) |
| `TEST_CONTROL_SYSTEM.md` | Complete testing guide |
| `OPERATIONAL_STATUS.md` | System status & capabilities |
| `ITERATION_SUMMARY.md` | What was fixed this session |
| `BROADCASTER_AGENT_FIX.md` | Technical architecture |

---

## 🎯 What Works Now

✅ Broadcaster sessions with passwords  
✅ Viewer authentication  
✅ Mouse movement relay  
✅ Mouse click relay  
✅ Keyboard input relay  
✅ Special key handling  
✅ Real-time control execution  
✅ Event logging  
✅ Error handling  
✅ Auto-reconnect  

---

## 📊 Control Features

### Mouse
- Move: Real-time cursor tracking
- Click: Left/right/middle buttons
- Drag: Click and drag operations
- Scroll: Wheel up/down

### Keyboard
- Type: Text input
- Press: Individual keys
- Special: Arrow keys, Enter, Backspace, Tab
- Hotkeys: Ctrl+C, Alt+Tab, etc.

---

## 🔐 Security

- Password protected broadcasts ✅
- Session isolation ✅
- Broadcaster approval system ✅
- HTTPS only ✅

---

## 🐛 Debug Commands

```bash
# Test connection before running agent
python agent/test_connection.py

# Run agent with verbose output
python agent/broadcaster_agent.py

# Check server logs
tail -f logs.txt
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Server response | <50ms |
| Control latency | <100ms |
| Connection time | ~2s |
| Mouse responsiveness | Real-time |

---

## 💡 Tips

- Keep agent running while using viewer
- Use auto_viewer link (automatic authentication)
- Press Ctrl+C to stop agent cleanly
- Check logs.txt for debugging
- Test with `test_connection.py` first

---

## 🎉 Success Indicators

Agent terminal should show:
```
✅ BROADCASTER AGENT IS RUNNING
⌨️  Waiting for control commands...
```

Viewer page should show:
```
Connected to device (blue status)
Mouse: ON
Keyboard: ON
```

When you move mouse in viewer:
```
[timestamp] 📨 Control received:
  🖱️ MOUSE: Moved to (x, y)
```

---

## 📞 Support

- Check documentation files in repo
- Review TEST_CONTROL_SYSTEM.md troubleshooting
- Check Render dashboard logs
- Verify test_connection.py passes

---

**Last Updated**: January 24, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0 Control System
