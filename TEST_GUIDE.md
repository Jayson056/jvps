# Quick Test Guide - Security Layer Implementation

## Pre-Test Setup

1. Navigate to project directory:
   ```bash
   cd c:\Users\USER\Documents\NewProject\BROADCAST
   ```

2. Start the server:
   ```bash
   python server/app.py
   ```
   
   You should see:
   ```
   [STARTUP] OmniStream Pro server starting on 0.0.0.0:5000
   ```

3. Open browser to: `http://localhost:5000`

---

## Test Case 1: Home Page → Setup Page

### Steps:
1. On home page, locate the "📺 Start Broadcasting" card
2. Click it
3. Verify you're redirected to setup page (`/brodcast_dets`)
4. Page shows form with fields:
   - "Room Name to Display"
   - "Broadcaster Name"
   - "Create Broadcast" button

**Expected Result:** ✅ Form displays correctly

---

## Test Case 2: Create Session with Credentials

### Steps:
1. On setup page, fill in form:
   - Room Name: `Test Broadcast`
   - Broadcaster Name: `Test User`
2. Click "Create Broadcast" button
3. Wait for API response (should be instant)

**Expected Result:** ✅ Credentials section appears with:
- Session ID (UUID format)
- Password (8 hex characters, e.g., A7F3B2E9)
- Auto-viewer link (contains /auto_viewer/)
- Manual view link (contains /view/)

---

## Test Case 3: File Generation

### Steps:
1. Complete Test Case 2
2. Check for new files in `c:\Users\USER\Documents\NewProject\BROADCAST\`:
   - `logs.txt`
   - `password.txt`

3. Open `logs.txt` - should contain:
   ```
   [YYYY-MM-DD HH:MM:SS] [STARTUP] OmniStream Pro server starting...
   [YYYY-MM-DD HH:MM:SS] [SESSION_CREATED] Room: Test Broadcast | Broadcaster: Test User...
   [YYYY-MM-DD HH:MM:SS] [PASSWORD_CREATED] Credentials saved...
   ```

4. Open `password.txt` - should contain:
   ```
   ======================================================================
   BROADCAST SESSION CREATED
   ======================================================================
   Timestamp:        YYYY-MM-DD HH:MM:SS
   Device ID:        <uuid>
   Session ID:       <uuid>
   Room Name:        Test Broadcast
   Broadcaster Name: Test User
   Password:         <8-char hex>
   Password Hash:    <sha256 hash>
   ======================================================================
   ```

**Expected Result:** ✅ Both files exist with properly formatted content

---

## Test Case 4: Copy Buttons

### Steps:
1. On setup page with visible credentials
2. Click "📋 Copy Auto-Link" button
3. Paste in notepad (Ctrl+V)
4. Verify URL format: `http://localhost:5000/auto_viewer/<session_id>?pwd=<password>`
5. Click "📋 Copy Manual-Link" button
6. Verify URL format: `http://localhost:5000/view/<session_id>`

**Expected Result:** ✅ Both buttons copy correct URLs

---

## Test Case 5: Redirect to Broadcaster View

### Steps:
1. On setup page with visible credentials
2. Click "🚀 Share Your Screen Now!" button
3. Verify redirect to `/broadcast/<device_id>`
4. Wait for page to fully load

**Expected Result:** ✅ Redirected to broadcaster view

---

## Test Case 6: Broadcaster View Displays Credentials

### Steps:
1. Complete Test Case 5 (should be on broadcaster view)
2. Scroll down to "📡 Connection Information" section
3. Verify you see:
   - Device ID box with UUID
   - Session ID box with UUID
   - **🔐 Broadcast Password** (red background) with 8-char hex password
   - **Auto-Connect Link** (green section) with shareable URL
   - **Manual View Link** (blue section) with shareable URL
   - "How Viewers Connect" explanation

4. Test copy buttons:
   - Click "📋 Copy Password" → paste in notepad
   - Click "📋 Copy Auto-Link" → paste in notepad
   - Click "📋 Copy Manual-Link" → paste in notepad

**Expected Result:** ✅ All credentials visible and copy buttons work

---

## Test Case 7: Multiple Sessions

### Steps:
1. Complete a full session (Test Cases 1-6)
2. Go back to home page: click "🏠 Back to Home"
3. Click "Start Broadcasting" again
4. Enter different credentials:
   - Room Name: `Test Broadcast 2`
   - Broadcaster Name: `Test User 2`
5. Create this second session
6. Open `password.txt`

**Expected Result:** ✅ `password.txt` contains both sessions with proper separation

---

## Test Case 8: Session Storage

### Steps:
1. Complete a session setup (create credentials)
2. Open Browser DevTools (F12)
3. Go to Application → Session Storage → http://localhost:5000
4. Verify entry `broadcastData` exists
5. Expand it and verify it contains:
   ```json
   {
     "roomName": "...",
     "broadcasterName": "...",
     "sessionId": "...",
     "password": "...",
     "deviceId": "...",
     "autoViewerLink": "...",
     "manualViewLink": "...",
     "broadcasterUrl": "..."
   }
   ```

**Expected Result:** ✅ Session storage contains all expected properties

---

## Test Case 9: Log Event Categories

### Steps:
1. Complete several sessions (Test Cases 1-6)
2. Open `logs.txt` and scan for these event types:
   - `STARTUP`
   - `SESSION_CREATED`
   - `PASSWORD_CREATED`
   - Any other events from device registration

**Expected Result:** ✅ Logs show variety of event types with timestamps

---

## Test Case 10: Browser Persistence

### Steps:
1. Complete Test Case 5 (on broadcaster view with credentials showing)
2. Note the credentials displayed
3. Refresh page (F5)
4. Verify credentials are still visible at same location

**Expected Result:** ✅ Credentials persist after page refresh (from sessionStorage)

---

## Troubleshooting

### Issue: "Session not found" error on setup page
- Check browser console (F12) for error details
- Verify server is running: `python server/app.py`
- Check server console for error messages

### Issue: Files not being created
- Verify write permissions in `c:\Users\USER\Documents\NewProject\BROADCAST\`
- Check Flask server console for permission errors
- Try running command prompt as Administrator

### Issue: Links not copying to clipboard
- Try different browser (Chrome, Firefox, Edge recommended)
- Enable "Insecure Clipboard" in DevTools settings
- Manual copy-paste as fallback

### Issue: Session data not persisting
- Check if cookies are enabled in browser
- Try different browser
- Clear browser cache and restart

### Issue: Credentials showing as "N/A"
- This is fallback behavior when sessionStorage is empty
- Ensure you're coming from setup page (not directly accessing broadcaster URL)
- Check browser console for JavaScript errors

---

## Expected Results Summary

| Test Case | Expected Status |
|-----------|-----------------|
| 1. Home → Setup | ✅ Redirects to /brodcast_dets |
| 2. Create Session | ✅ Credentials display immediately |
| 3. File Generation | ✅ Both logs.txt and password.txt created |
| 4. Copy Buttons | ✅ All copy buttons work correctly |
| 5. Broadcaster Redirect | ✅ Redirects to /broadcast/<device_id> |
| 6. Display Credentials | ✅ Password and links visible at bottom |
| 7. Multiple Sessions | ✅ password.txt contains all sessions |
| 8. Session Storage | ✅ broadcastData stored in sessionStorage |
| 9. Log Events | ✅ Various event types logged with timestamps |
| 10. Persistence | ✅ Credentials show after page refresh |

---

## Performance Notes

- API response time: < 100ms
- File write time: < 10ms
- Page load time: < 500ms (including CSS/JS)
- Broadcaster view initialization: < 1s

---

## Next Steps After Verification

1. ✅ Verify all 10 test cases pass
2. ✅ Review logs.txt for proper event logging
3. ✅ Review password.txt for credential storage format
4. ✅ Test with multiple concurrent sessions (open multiple browser windows)
5. ✅ Test viewer connection with generated links
6. ✅ Test error handling (invalid form inputs, API errors)
7. Deploy to production with HTTPS enabled

---

## Support

If any test case fails:
1. Check the `logs.txt` file for error details
2. Review browser console (F12) for client-side errors
3. Check Flask server console for backend errors
4. Refer to IMPLEMENTATION_NOTES.md for detailed documentation
5. Verify file permissions in project directory

