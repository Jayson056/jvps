# JVPS Domain Configuration - http://jvps.onrender.com

## Overview
The application is now configured to use the production domain **http://jvps.onrender.com** for all generated shareable links.

---

## URL Formats

### 1. Direct Access Link (Auto-Viewer)
**Format**: `http://jvps.onrender.com/auto_viewer/{SESSION_ID}?pwd={PASSWORD}`

**Example**: `http://jvps.onrender.com/auto_viewer/SESSION-E78C2A77D89F114030B0C5BC?pwd=E86ED7D3`

**Features**:
- Automatic connection with password
- No login screen required
- Direct access to remote desktop
- Full mouse and keyboard control immediately available

---

### 2. Manual/Secure Access Link
**Format**: `http://jvps.onrender.com/view/{SESSION_ID}`

**Example**: `http://jvps.onrender.com/view/SESSION-E78C2A77D89F114030B0C5BC`

**Features**:
- User must enter password to connect
- Additional security layer
- Redirects to password prompt page
- User explicitly authorizes access

---

### 3. Broadcaster/Host View
**Format**: `http://jvps.onrender.com/broadcast/{DEVICE_ID}`

**Example**: `http://jvps.onrender.com/broadcast/DEVICE-ABC123`

**Features**:
- Shows active connection status
- Displays connected users
- Provides sharing links
- Allows session management

---

## Domain Configuration Details

### Backend Implementation (server/app.py)

The application automatically detects the environment:

```python
# Production domain for Render
production_domain = "http://jvps.onrender.com"

# Logic to determine which domain to use
if request.host.startswith('localhost') or request.host.startswith('127.0.0.1'):
    base_url = request.host_url.rstrip('/')  # Local development
else:
    base_url = production_domain  # Production (Render)
```

### Benefits

✅ **Automatic Detection** - Works in both local and production environments
✅ **Consistent Links** - All generated links use the same domain
✅ **Easy Sharing** - Users get clean, professional URLs
✅ **No Dynamic Changes** - Links remain valid regardless of where app is accessed from

---

## Environment Support

### Development Environment (Local)
- **Detected**: `localhost`, `127.0.0.1`
- **Example Link**: `http://localhost:5000/auto_viewer/SESSION-ID?pwd=PASSWORD`

### Production Environment (Render)
- **Detected**: Any non-localhost domain
- **Example Link**: `http://jvps.onrender.com/auto_viewer/SESSION-ID?pwd=PASSWORD`
- **Domain**: `http://jvps.onrender.com`

---

## Session Link Generation Process

### When Broadcasting Starts

1. **User creates a session** via `/api/create_session`
2. **Backend generates**:
   - Unique Session ID
   - Secure Password (6 characters)
   - Device ID
3. **Backend detects environment**:
   - If `localhost` → Use local URL
   - If other host → Use `http://jvps.onrender.com`
4. **Backend generates links**:
   - Auto-viewer link with password
   - Manual view link (password required at connection)
5. **Frontend receives**:
   ```json
   {
       "success": true,
       "session_id": "SESSION-E78C2A77D89F114030B0C5BC",
       "password": "E86ED7D3",
       "auto_viewer_link": "http://jvps.onrender.com/auto_viewer/SESSION-E78C2A77D89F114030B0C5BC?pwd=E86ED7D3",
       "manual_viewer_link": "http://jvps.onrender.com/view/SESSION-E78C2A77D89F114030B0C5BC"
   }
   ```
6. **Links are displayed** to user for sharing

---

## Link Usage Flow

### Auto-Viewer Link (Direct Access)
```
User clicks link
    ↓
Browser navigates to: http://jvps.onrender.com/auto_viewer/{ID}?pwd={PWD}
    ↓
Session auto-loads with password
    ↓
WebRTC connection established automatically
    ↓
User has immediate control of remote desktop
```

### Manual View Link (Secure Access)
```
User clicks link
    ↓
Browser navigates to: http://jvps.onrender.com/view/{ID}
    ↓
Password entry page displayed
    ↓
User enters password manually
    ↓
Backend validates password
    ↓
WebRTC connection established
    ↓
User has control of remote desktop
```

---

## API Response Example

### Create Session API Response

**Endpoint**: `POST /api/create_session`

**Response**:
```json
{
    "success": true,
    "device_id": "DEVICE-ABC123DEF456",
    "session_id": "SESSION-E78C2A77D89F114030B0C5BC",
    "password": "E86ED7D3",
    "room_name": "My Desktop",
    "broadcaster_name": "John",
    "auto_viewer_link": "http://jvps.onrender.com/auto_viewer/SESSION-E78C2A77D89F114030B0C5BC?pwd=E86ED7D3",
    "manual_viewer_link": "http://jvps.onrender.com/view/SESSION-E78C2A77D89F114030B0C5BC",
    "broadcaster_url": "http://jvps.onrender.com/broadcast/DEVICE-ABC123DEF456"
}
```

---

## Sharing Instructions for Users

### Easy Sharing Method
1. Create a broadcast session
2. Copy the **Direct Access Link** (Auto-Viewer)
3. Share via email, message, or link
4. Remote user clicks the link
5. Connection established instantly

### Secure Sharing Method
1. Create a broadcast session
2. Copy the **Secure Access Link** (Manual View)
3. Send link to user
4. Separately send password via another channel
5. User enters password to connect

---

## Configuration File Reference

### Location
- **File**: `server/app.py`
- **Lines**: 104-114 (URL generation logic)

### Production Domain Setting
```python
production_domain = "http://jvps.onrender.com"  # Change here if needed
```

### To Change Domain
1. Edit `server/app.py`
2. Update `production_domain` variable
3. Restart the application
4. Generate new links

---

## Testing URLs

### Test Direct Access
```
http://jvps.onrender.com/auto_viewer/SESSION-E78C2A77D89F114030B0C5BC?pwd=E86ED7D3
```

### Test Manual Access
```
http://jvps.onrender.com/view/SESSION-E78C2A77D89F114030B0C5BC
(Then enter password: E86ED7D3)
```

### Test Local Development
```
http://localhost:5000/auto_viewer/SESSION-ID?pwd=PASSWORD
http://localhost:5000/view/SESSION-ID
```

---

## Troubleshooting

### Links Show Wrong Domain
- **Check**: Is the app running on Render or localhost?
- **Local**: Links should show `http://localhost:PORT`
- **Remote**: Links should show `http://jvps.onrender.com`

### Links Not Working
1. Verify session ID is valid
2. Check password is included in auto-viewer links
3. Confirm domain is accessible
4. Check firewall/network restrictions

### Domain Access Blocked
1. Check Render deployment status
2. Verify domain DNS resolution
3. Test connectivity to jvps.onrender.com
4. Check browser console for errors

---

## Security Notes

🔐 **Password Protection**
- Auto-viewer links include password in URL (convenient, less secure)
- Manual view requires password entry (more secure)
- Passwords are unique per session
- Passwords are not stored long-term

🔒 **Session IDs**
- Unique per broadcast session
- Format: SESSION-{24-character hex string}
- No two sessions share the same ID

🛡️ **Best Practices**
- Use manual view link for sensitive content
- Share links over secure channels
- Generate new sessions for each use
- Monitor connected users

---

## Version Information

- **Configuration Version**: 1.0
- **Domain**: http://jvps.onrender.com
- **Implementation Date**: January 24, 2026
- **Status**: ✅ Active and Production Ready

---

## Support

For domain configuration questions:
1. Review this guide
2. Check `server/app.py` for URL generation logic
3. Verify Render deployment settings
4. Test with local and production environments

