# 🧪 OmniStream Pro v2 - Testing Guide

## ✅ Pre-Flight Checklist

Before you start:
- [ ] PyAutoGUI is installed: `pip install pyautogui`
- [ ] Flask & dependencies installed: `pip install -r requirements.txt`
- [ ] Port 58247 is free: `netstat -ano | findstr :58247`
- [ ] You have 2 devices or 2 browser windows for testing

---

## 🚀 Step-by-Step Testing

### **Step 1: Start the Server**

```powershell
cd C:\Users\USER\Documents\NewProject\BROADCAST
python app.py
```

**Expected Output:**
```
[INFO] Starting OmniStream Pro server...
 * Debugger is active!
 * Debugger PIN: 397-338-059
(19860) wsgi starting up on http://0.0.0.0:58247
```

✅ **PASS:** Server is running and listening on port 58247

---

### **Step 2: Open Home Page**

Browser 1: `http://localhost:58247/`

**Should See:**
- ✓ OmniStream Pro logo
- ✓ "Start Broadcasting" button
- ✓ "Watch Live" button
- ✓ Feature list

Click **"Start Broadcasting"**

---

### **Step 3: Broadcaster Setup**

**Expected Page Elements:**
- ✓ Status banner saying "Broadcast is LIVE"
- ✓ Black video box (waiting for screen permission)
- ✓ Device ID in a code box
- ✓ Auto-Viewer URL in a code box
- ✓ "Copy Auto-Viewer Link" button
- ✓ "Stop Broadcast" button

**Permission Dialog:**
- Browser asks to share screen
- Click "Allow"

**Expected Result:**
- Video preview fills with your screen
- No errors in console (F12)

✅ **PASS:** Broadcaster can see their screen

---

### **Step 4: Test Auto-Viewer Link**

**On Broadcaster Page:**
1. Click **"Copy Auto-Viewer Link"** button
2. Alert says "✓ Link copied to clipboard!"

**Open New Browser/Window:**
- Browser 2: Paste the link (Ctrl+V in address bar)
- Press Enter

**Expected:**
- Status shows "Connecting..."
- Screen from Browser 1 appears
- Status changes to "Connected" (green dot)

✅ **PASS:** Viewer can see broadcaster's screen

---

### **Step 5: Test Mouse Control**

**On Viewer (Browser 2):**
1. Move mouse over the video
2. Click on a button/element on the broadcasted screen

**Expected on Broadcaster (Browser 1 or actual screen):**
- ⌚ Cursor moves to where you hovered
- 🖱️ Elements respond to clicks
- Mouse cursor position updates every ~100-150ms

✅ **PASS:** Mouse control works

---

### **Step 6: Test Keyboard Control**

**On Viewer (Browser 2):**
1. Click on the video to focus it
2. Type something (e.g., "hello")

**Expected on Broadcaster (Browser 1 or actual screen):**
- ⌨️ Text appears where keyboard input was sent
- Arrow keys move cursors
- Special keys work (Enter, Backspace, etc.)

✅ **PASS:** Keyboard control works

---

### **Step 7: Test Control Toggles**

**On Viewer (Browser 2):**
1. Click **"🖱️ Mouse: ON"** button
2. Move mouse - should NOT move on broadcaster

**Expected:**
- Button text changes to **"Mouse: OFF"**
- Button color changes to warning (orange/yellow)

1. Move mouse again - nothing happens on broadcaster
2. Click button again to toggle back to "ON"
3. Mouse control resumes

✅ **PASS:** Toggle buttons work

**Repeat for Keyboard toggle:**
1. Type something with keyboard control ON - it works
2. Click "⌨️ Kbd: ON" to toggle OFF
3. Type again - nothing happens
4. Toggle back ON

---

### **Step 8: Check Latency Display**

**On Viewer (Browser 2):**
- Look at top right corner
- Should show: `Latency: XXXms` (updates every 2 seconds)

**Expected Values:**
- Local network: 10-50ms ✅
- WiFi: 20-100ms ✅
- Internet: 100-500ms ⚠️

✅ **PASS:** Latency tracking works

---

### **Step 9: Test Fullscreen**

**On Viewer (Browser 2):**
1. Click **"🖥️ Fullscreen"** button
2. Press ESC to exit fullscreen

**Expected:**
- Video goes fullscreen
- All controls visible
- Still works in fullscreen

✅ **PASS:** Fullscreen works

---

### **Step 10: Test Disconnect & Reconnect**

**Current State:**
- Browser 1: Broadcasting
- Browser 2: Viewing

**Test:**
1. Close Browser 2 tab
2. Server logs should show: `[INFO] Device disconnected: ...`
3. Refresh Browser 2 and paste auto-viewer URL again
4. Should reconnect instantly

✅ **PASS:** Reconnection works

---

## 🔍 Server Console Log Analysis

### **Good Log Output:**

```
[INFO] New session created: 596d332e-...
[INFO] Broadcaster registered with ID: 596d332e-...
[INFO] Viewer registered with ID: f4938ea0-...
[INFO] Viewer f4938ea0-... joined session 596d332e-...
[INFO] Relaying control input to broadcaster 596d332e-...
[INFO] Relaying control input to broadcaster 596d332e-...
```

✅ All controls are being relayed

### **Bad Log Output:**

```
[ERROR] No broadcaster found for session...
[ERROR] Broadcaster not registered in devices
[ERROR] Broadcaster has no SID assigned
```

❌ Control signals aren't reaching the broadcaster

---

## 🐛 Troubleshooting During Testing

### **Issue: Video Won't Share (Black Box)**

**Cause:** Screen capture permission denied

**Fix:**
1. Close browser and reopen
2. Click "Allow" when permission dialog appears
3. Make sure you selected the correct monitor (not "Application Window")

---

### **Issue: Mouse Doesn't Move**

**Cause 1:** Status shows "Disconnected"
- Solution: Refresh both pages

**Cause 2:** "Mouse: OFF" button is active
- Solution: Click to turn ON

**Cause 3:** PyAutoGUI blocked by Windows
- Solution: Run Flask as Administrator

---

### **Issue: Keyboard Types on Viewer Instead of Broadcaster**

**Cause:** Focus is on input box in viewer

**Fix:** Click on the video preview to focus it, then type

---

### **Issue: Links Keep Showing "Session Not Found"**

**Cause:** Broadcaster closed/crashed

**Fix:**
1. Go back to home page
2. Click "Start Broadcasting" again
3. Copy new link and test

---

## 📊 Performance Testing

### **Test 1: Latency Under Load**

```
1. Start broadcasting
2. Move mouse rapidly back and forth
3. Type continuously while moving mouse
4. Watch latency display
```

**Expected:** Should still be <200ms even under load

---

### **Test 2: Multiple Viewers** (Advanced)

```
1. Start broadcast (Browser 1)
2. Connect Viewer 1 (Browser 2)
3. Connect Viewer 2 (Browser 3)
4. Control from Viewer 1 - works
5. Control from Viewer 2 - queues behind Viewer 1 (normal)
```

Expected: Both viewers see screen, but control inputs may queue

---

### **Test 3: Network Across Computers**

```
1. Note Server IP: ipconfig (look for IPv4)
2. On other computer, go to: http://[YOUR-IP]:58247/
3. Follow same steps as local testing
```

Expected: Works but latency ~50-200ms depending on network

---

## ✨ Advanced Testing

### **Test: Broadcast Quality**

**Method:** Look at settings → Chrome DevTools → Network

**Check:**
- Video bitrate: ~2-5 Mbps (good)
- Framerate: 30fps (good)
- Packet loss: 0% (good)

---

### **Test: CPU Usage**

**Method:** Open Task Manager

**Expected:**
- Flask process: 10-20% CPU during streaming
- Python: 2-5% CPU for control handling
- Browser: 15-30% CPU for video decoding

---

## ✅ Final Validation Checklist

- [ ] Server starts without errors
- [ ] Home page loads
- [ ] Broadcast page shows video
- [ ] Auto-viewer link works
- [ ] Mouse movement works
- [ ] Keyboard input works
- [ ] Control toggles work
- [ ] Latency displays correctly
- [ ] Fullscreen works
- [ ] Disconnect/reconnect works
- [ ] Logs show proper flow
- [ ] No errors in browser console
- [ ] No errors in server console

---

## 🎯 Next Steps After Testing

1. **Share with Team:** Copy auto-viewer link to coworkers
2. **Test Across Network:** Use from different computer
3. **Test Mobile:** Try from phone/tablet (may need fullscreen)
4. **Customize:** Adjust MOUSE_SPEED and settings
5. **Deploy:** Consider cloud hosting for remote use
6. **Add Auth:** Implement user login for production

---

## 📞 Debug Mode

To see more detailed logging, edit `app.py`:

```python
# Add at the top after imports:
import logging
logging.basicConfig(level=logging.DEBUG)

# Add before socketio.run():
app.logger.setLevel(logging.DEBUG)
```

---

## 🎉 Congratulations!

If you've passed all tests, **OmniStream Pro v2 is working perfectly!**

You can now:
✅ Share your screen with anyone
✅ Let them control your mouse & keyboard
✅ Monitor latency and connection status
✅ Toggle controls on/off for safety
✅ Fullscreen for presentations

**Happy streaming! 🎬**

