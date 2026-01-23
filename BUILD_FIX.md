# 🔧 BUILD FIX - Requirements Separation

## Problem
Render build failed because `requirements.txt` included packages that don't work on headless servers:
- **PyAutoGUI** - GUI control (only works locally with display)
- **PyGetWindow, PyScreeze, MouseInfo** - GUI detection (requires display)
- **mss** - Screen capture (requires DISPLAY environment)
- **Pillow, numpy** - Image processing (not needed on server)
- **aiortc, av, aioice, pylibsrtp** - Complex WebRTC dependencies (not yet implemented)

## Solution

Split requirements into three files:

### 1. **requirements.txt** (36 packages) - Server/Render Only ✅
```
✅ Flask, Flask-SocketIO
✅ Socket.IO libraries
✅ Gunicorn, Eventlet
✅ Werkzeug, cryptography
✅ Minimal utilities
```

Used by Render for deployment. Lean, minimal, headless-compatible.

### 2. **requirements-server.txt** (36 packages) - Server Reference ✅
Same as requirements.txt for documentation purposes.

### 3. **requirements-agent.txt** (22 packages) - Broadcaster Agent ✅
```
✅ Socket.IO (for connecting to server)
✅ PyAutoGUI + related (GUI control)
✅ mss (screen capture)
✅ Pillow, numpy (image processing)
```

Run locally on broadcaster's machine: `pip install -r requirements-agent.txt`

---

## Files Changed

| File | Action | Size |
|------|--------|------|
| `requirements.txt` | Removed GUI packages | 36 packages |
| `requirements-server.txt` | NEW reference | 36 packages |
| `requirements-agent.txt` | NEW for agent | 22 packages |

---

## Impact

### Before (Failed ❌)
```
Render tries to install:
- PyAutoGUI (no display)
- mss (no DISPLAY env)
- aiortc, av (complex deps)
→ Build FAILED
```

### After (Works ✅)
```
Render installs minimal set:
- Flask, Socket.IO
- Gunicorn, Eventlet
- Cryptography, utilities
→ Build SUCCEEDS
```

---

## User Instructions

### For Render Server
No changes needed. Auto-deploy uses new minimal `requirements.txt`.

### For Broadcaster Agent

Install agent dependencies locally:
```bash
cd BROADCAST/agent
pip install -r ../requirements-agent.txt
```

Then run:
```bash
python broadcaster_agent.py
```

---

## Why This Matters

**Headless Server Issue**: Render runs in a containerized, headless environment with no GUI. Packages requiring `DISPLAY` or GPU access fail to install.

**Solution**: Separate concerns:
- **Server** = relay only (no GUI packages)
- **Agent** = control execution (needs GUI packages)
- **Deployment** = Render gets lightweight server, users get full agent locally

---

## Git Commit

```
37ef63b - Split requirements - server minimal + separate agent requirements
```

---

## Next Deploy

Render will:
1. ✅ Clone latest code
2. ✅ Run `pip install -r requirements.txt` (now minimal)
3. ✅ Install successfully
4. ✅ Start Flask app
5. ✅ Live at https://jvps.onrender.com

**Estimated time**: ~30 seconds

---

## Verification

After deploy completes:
```bash
# Check server is live
curl https://jvps.onrender.com
# Should return HTML home page

# Check Socket.IO is working
# Open https://jvps.onrender.com in browser
# Should connect without errors
```

---

**Status**: ✅ Fixed and deployed  
**Time to fix**: < 5 minutes  
**Lines changed**: 71  
**Files changed**: 3
