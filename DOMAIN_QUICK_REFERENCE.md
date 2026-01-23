# JVPS Domain Update - Quick Reference

## ✅ Changes Completed

### Production Domain Configuration
- **Default Domain**: `http://jvps.onrender.com`
- **Auto-Detect**: Works locally and on production
- **Status**: ✅ Implemented and Ready

---

## Generated URL Examples

### Direct Access (Auto-Viewer)
```
http://jvps.onrender.com/auto_viewer/SESSION-E78C2A77D89F114030B0C5BC?pwd=E86ED7D3
```
- Password included in URL
- Auto-connects on click
- Full control immediately available

### Secure Access (Manual View)
```
http://jvps.onrender.com/view/SESSION-E78C2A77D89F114030B0C5BC
```
- Password required at login
- Extra security layer
- User must authenticate

### Broadcaster View
```
http://jvps.onrender.com/broadcast/DEVICE-ABC123DEF456
```
- Shows session status
- Displays connected users
- Provides sharing links

---

## How It Works

### URL Generation Logic (server/app.py lines 104-114)

```python
# Production domain
production_domain = "http://jvps.onrender.com"

# Environment detection
if request.host.startswith('localhost') or request.host.startswith('127.0.0.1'):
    base_url = request.host_url.rstrip('/')  # Local: http://localhost:5000
else:
    base_url = production_domain  # Production: http://jvps.onrender.com
```

### Environment Support

| Environment | Detection | Domain | Example |
|-------------|-----------|--------|---------|
| Local Dev | localhost, 127.0.0.1 | http://localhost:5000 | http://localhost:5000/auto_viewer/ID?pwd=PASS |
| Production | Other hosts | http://jvps.onrender.com | http://jvps.onrender.com/auto_viewer/ID?pwd=PASS |

---

## Files Modified

### Backend
- ✅ `server/app.py` (lines 104-114)
  - Updated URL generation logic
  - Implemented domain detection
  - Set production domain to `http://jvps.onrender.com`

### Frontend
- ✅ `templates/brodcast_dets.html`
  - Displays links from backend API
  - No changes needed (already receives from backend)

- ✅ `templates/brodview_screen.html`
  - Displays shared links
  - No changes needed (already receives from backend)

---

## API Response Format

### POST /api/create_session

**Response Body**:
```json
{
    "success": true,
    "session_id": "SESSION-E78C2A77D89F114030B0C5BC",
    "password": "E86ED7D3",
    "device_id": "DEVICE-ABC123",
    "room_name": "My Desktop",
    "broadcaster_name": "John",
    "auto_viewer_link": "http://jvps.onrender.com/auto_viewer/SESSION-E78C2A77D89F114030B0C5BC?pwd=E86ED7D3",
    "manual_viewer_link": "http://jvps.onrender.com/view/SESSION-E78C2A77D89F114030B0C5BC",
    "broadcaster_url": "http://jvps.onrender.com/broadcast/DEVICE-ABC123"
}
```

---

## User Experience Flow

### Step 1: Create Session
- User enters device name
- Clicks "Create Session"
- Backend generates session with new domain URLs

### Step 2: See Generated Links
- Auto-Viewer link with password included
- Manual View link (password required)
- Both use `http://jvps.onrender.com` domain

### Step 3: Share Links
- User copies and shares links
- Recipients click links
- Connect to remote desktop

---

## Testing

### Local Testing
```
http://localhost:5000/auto_viewer/SESSION-ID?pwd=PASSWORD
http://localhost:5000/view/SESSION-ID
```

### Production Testing
```
http://jvps.onrender.com/auto_viewer/SESSION-ID?pwd=PASSWORD
http://jvps.onrender.com/view/SESSION-ID
```

---

## Key Features

✨ **Automatic Detection**
- No configuration needed
- Works in all environments
- Smart domain selection

🔗 **Clean URLs**
- Professional format
- Easy to share
- Standard routing paths

🔒 **Secure**
- Unique session IDs
- Password protection
- One-time use sessions

📱 **User-Friendly**
- Simple to understand
- Easy to share via link
- Works on all devices

---

## Configuration

### To Change Production Domain

**File**: `server/app.py` (line 107)

**Current**:
```python
production_domain = "http://jvps.onrender.com"
```

**To Update**:
```python
production_domain = "https://your-new-domain.com"  # With or without trailing slash
```

**Then**:
1. Restart the Flask application
2. Generate new session links
3. Test with new domain

---

## Troubleshooting

### Problem: Links show wrong domain
**Solution**: Check if running on localhost or Render
- Local: Should show `http://localhost:PORT`
- Render: Should show `http://jvps.onrender.com`

### Problem: Links not working
**Solution**:
1. Verify domain is accessible
2. Check session ID is valid
3. Confirm password is correct
4. Test domain in browser directly

### Problem: Auto-connect not working
**Solution**:
- Check password is included in URL (`?pwd=`)
- Verify session hasn't expired
- Check browser console for errors

---

## Documentation

- 📄 **DOMAIN_CONFIGURATION.md** - Complete domain setup guide
- 📄 **DESIGN_REFINEMENT.md** - Design system changes
- 📄 **DESIGN_COMPLETE.md** - Quick design summary

---

## Version Info

- **Update Date**: January 24, 2026
- **Domain**: http://jvps.onrender.com
- **Status**: ✅ Production Ready

---

## Summary

✅ Production domain configured  
✅ Auto-detection implemented  
✅ URL format standardized  
✅ All links now use `http://jvps.onrender.com`  
✅ Backward compatible with localhost  
✅ Ready for deployment  

