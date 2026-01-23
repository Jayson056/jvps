# Security Implementation - Flow Diagrams

## Complete Broadcasting Flow with Security

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OMNISTREAM PRO - SECURITY FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════
PHASE 1: BROADCASTER SETUP (NEW SECURITY LAYER)
════════════════════════════════════════════════════════════════════════════════

    ┌─────────────────────┐
    │   Home Page         │ ← http://localhost:5000/
    │  (/)                │
    └──────────┬──────────┘
               │
               │ Click "Start Broadcasting"
               ▼
    ┌──────────────────────────────────┐
    │  Broadcast Setup Page            │ ← /brodcast_dets (NEW)
    │  (brodcast_dets.html)            │
    │                                  │
    │  [Input: Room Name]              │
    │  [Input: Broadcaster Name] (opt) │
    └──────────┬───────────────────────┘
               │
               │ Click "Create Session"
               ▼
    ┌──────────────────────────────────────────────┐
    │  Generate Session Credentials:              │
    │                                              │
    │  Session ID ──────→ SESSION-ABC1234567      │
    │  Password   ──────→ X4Q8J2P9 (8-char)      │
    │  Device ID  ──────→ DEV-KL9N2Q4X           │
    │                                              │
    │  ✓ Credentials Displayed & Copyable         │
    │  ✓ Two Shareable Links Generated            │
    └──────────┬───────────────────────────────────┘
               │
               │ Click "Share Your Screen Now"
               ▼
    ┌──────────────────────────────────────────────┐
    │  Broadcaster View                            │
    │  (brodview_screen.html)                      │
    │                                              │
    │  ✓ Display Session Info                     │
    │  ✓ Request Screen Capture Permission        │
    │  ✓ Start Broadcasting Stream                │
    │  ✓ Show Active Viewers List                 │
    │  ✓ Display Shareable Links                  │
    └──────────┬───────────────────────────────────┘
               │
               │ Broadcasting Active!
               ▼
    ┌──────────────────────────────────────────────┐
    │  Socket.IO Connection Established           │
    │  • Device registered as 'broadcaster'       │
    │  • Session credentials stored server-side   │
    │  • Waiting for viewer connections           │
    └──────────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════════════════
PHASE 2: VIEWER ACCESS (AUTO-VIEWER - INSTANT)
════════════════════════════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────────┐
    │  Broadcaster shares Auto-Viewer Link:       │
    │  http://localhost:5000/                     │
    │  auto_viewer/SESSION-ABC1234567?pwd=X4Q8J2P9
    └──────────┬────────────────────────────────┘
               │
               │ Viewer clicks the link
               ▼
    ┌──────────────────────────────────────────────┐
    │  Auto-Viewer Page (auto_viewer.html)        │ ← /auto_viewer/SESSION_ID?pwd=PASSWORD (NEW)
    │                                              │
    │  • Password auto-populated from URL         │
    │  • No user input required                   │
    │  • Auto-connects to broadcaster            │
    └──────────┬───────────────────────────────────┘
               │
               │ Socket.IO Register & Join
               ▼
    ┌──────────────────────────────────────────────┐
    │  WebRTC Connection Establishment            │
    │                                              │
    │  1. Viewer registers as 'viewer'           │
    │  2. Requests to join session               │
    │  3. Broadcaster auto-approves             │
    │  4. WebRTC peer connection established    │
    │  5. Stream received & displayed           │
    └──────────┬───────────────────────────────────┘
               │
               │ ✓ Connected!
               ▼
    ┌──────────────────────────────────────────────┐
    │  Viewer Can:                                │
    │  • See broadcaster's screen in real-time   │
    │  • Move mouse (remote control)             │
    │  • Click (mouse clicks sent to broadcaster)│
    │  • Type (keyboard input sent)              │
    │  • Monitor latency                         │
    └──────────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════════════════
PHASE 3: VIEWER ACCESS (MANUAL VIEW - PASSWORD PROTECTED)
════════════════════════════════════════════════════════════════════════════════

    ┌────────────────────────────────────┐
    │  Broadcaster shares Manual Link:   │
    │  http://localhost:5000/            │
    │  view_list?session=SESSION-ABC1234567
    └──────────┬─────────────────────────┘
               │
               │ Viewer clicks the link
               ▼
    ┌──────────────────────────────────────────────┐
    │  View List or View Screen Page              │
    │  (view_list.html / view_screen.html)        │
    │                                              │
    │  [Password Input Field]                    │
    │  [Connect Button]                          │
    └──────────┬───────────────────────────────────┘
               │
               │ Enter password & click Connect
               ▼
    ┌──────────────────────────────────────────────┐
    │  Password Verification (SERVER-SIDE)        │
    │                                              │
    │  POST /verify_password/SESSION-ABC1234567   │
    │  {password: "X4Q8J2P9"}                     │
    └──────────┬───────────────────────────────────┘
               │
         ┌─────┴──────┐
         │             │
         ▼             ▼
    ┌─────────┐   ┌─────────┐
    │ CORRECT │   │ INVALID │
    │PASSWORD │   │PASSWORD │
    └────┬────┘   └────┬────┘
         │             │
         ▼             ▼
    ┌─────────────┐   ┌──────────────────┐
    │ Proceed to  │   │ Error Message    │
    │ WebRTC      │   │ "Access Denied"  │
    │ Connection  │   │ Return to Login  │
    └─────────────┘   └──────────────────┘


════════════════════════════════════════════════════════════════════════════════
DATA FLOW DIAGRAM
════════════════════════════════════════════════════════════════════════════════

    BROADCASTER CLIENT                 SERVER                    VIEWER CLIENT
    (Browser)                          (Flask)                   (Browser)
         │                                │                           │
         │ 1. Click "Start Broadcast"     │                           │
         ├──────────────────────────────→ │                           │
         │                                │                           │
         │ 2. Go to /brodcast_dets        │                           │
         │ (Setup page)                   │                           │
         ├──────────────────────────────→ │                           │
         │                                │                           │
         │ 3. Generate Credentials        │                           │
         │ (CLIENT-SIDE)                  │                           │
         │ • Session ID                   │                           │
         │ • Password (8 char)            │                           │
         │ • Device ID                    │                           │
         │                                │                           │
         │ 4. Click "Share Screen Now"    │                           │
         ├──────────────────────────────→ /broadcast/DEV-XXX          │
         │                                │                           │
         │ 5. Socket.IO register_device   │                           │
         │ (Send credentials)             │                           │
         ├──────────────────────────────→ │                           │
         │                                │ Store in                  │
         │                                │ broadcast_sessions        │
         │                                │                           │
         │ 6. Screen capture              │                           │
         │ GetDisplayMedia()              │                           │
         ├──────────────────────────────→ │                           │
         │                                │                           │
         │                                │←──────── Auto-Viewer Link
         │                                │         (password in URL)
         │                                │                           │
         │                                │         Share URL         │
         │                                │←──────────────────────────┤
         │                                │                           │
         │ 7. Viewer joins               │                           │
         │ Socket.IO join_session         │────────────→ /auto_viewer/...
         ├──────────────────────────────→ │←─ Auto-connects          │
         │                                │                           │
         │ 8. WebRTC Offer/Answer         │                           │
         │ Signaling                      │─────────────────────────→ │
         ├──────────────────────────────→ │←───────────────────────┤
         │                                │                           │
         │ 9. ICE Candidates              │                           │
         ├────────────────────────────────────────────────────────→ │
         │                                │                           │
         │ 10. WebRTC Stream (P2P)        │                           │
         ├─────────────────────────────────────────────────────────→ │
         │                                │                           │
         │ 11. Control Input (Mouse/Kbd)  │                           │
         │ Socket.IO control_input        │←────────────────────────┤
         ├────────────────────────────────←───────────────────────────┤
         │                                │                           │
    BROADCASTING ACTIVE                  │              CONNECTED & CONTROLLING
         │                                │                           │


════════════════════════════════════════════════════════════════════════════════
SERVER STORAGE STRUCTURE
════════════════════════════════════════════════════════════════════════════════

devices = {
    'DEV-KL9N2Q4X': {
        'role': 'broadcaster',
        'sid': 'socket_id_12345',
        'approved': True
    },
    'DEV-AB3XY1Z9': {
        'role': 'viewer',
        'sid': 'socket_id_67890',
        'approved': True
    }
}

broadcast_sessions = {
    'DEV-KL9N2Q4X': {
        'session_id': 'SESSION-ABC1234567',
        'password': 'X4Q8J2P9',
        'room_name': 'My Test Room',
        'broadcaster_name': 'John Doe'
    }
}

sessions = {
    'SESSION-ABC1234567': {
        'broadcaster': 'DEV-KL9N2Q4X',
        'viewers': ['DEV-AB3XY1Z9'],
        'password': 'X4Q8J2P9',
        'room_name': 'My Test Room'
    }
}


════════════════════════════════════════════════════════════════════════════════
ERROR HANDLING FLOWS
════════════════════════════════════════════════════════════════════════════════

❌ Screen Capture Denied
    ├─ User clicks "Deny" on browser permission
    ├─ Alert: "Screen capture is required for broadcasting"
    └─ User returns to setup page

❌ Wrong Password
    ├─ Viewer enters incorrect password
    ├─ POST /verify_password returns 401
    ├─ Error: "Invalid password"
    └─ Viewer prompted to retry

❌ Session Not Found
    ├─ Viewer tries to access non-existent session
    ├─ Backend returns 404
    ├─ Error: "Session not found"
    └─ Redirect to view_list

❌ Broadcaster Disconnected
    ├─ Broadcaster closes browser/stops sharing
    ├─ Socket.IO disconnect event triggered
    ├─ Sessions cleaned up from server
    └─ Viewer sees "Broadcast ended"

❌ Network Connection Lost
    ├─ Viewer loses internet connection
    ├─ WebRTC peer connection drops
    ├─ Auto-reconnect attempts (optional feature)
    └─ Status: "Disconnected"


════════════════════════════════════════════════════════════════════════════════
SECURITY CHECKPOINTS
════════════════════════════════════════════════════════════════════════════════

✓ Checkpoint 1: Session Generation
  - Server validates room name (3-50 chars)
  - Auto-generates cryptographically-sound password
  - Creates unique session ID
  
✓ Checkpoint 2: Device Registration
  - Device gets unique ID
  - Session credentials stored server-side
  - Only broadcaster gets full access
  
✓ Checkpoint 3: Viewer Connection
  - Viewer must provide correct password (auto-viewer) OR
  - Viewer must enter password (manual view)
  - Server validates before granting access
  
✓ Checkpoint 4: WebRTC Signaling
  - Only registered devices can signal
  - Broadcaster auto-approves auto-viewer connections
  - Manual viewers require password approval
  
✓ Checkpoint 5: Control Input
  - Control commands only accepted from approved viewers
  - Socket.IO room isolation prevents cross-session interference

```

## Route Map

```
http://localhost:5000/
├── /                          → Home page with action cards
├── /brodcast_dets             → NEW: Broadcast setup page
├── /broadcast/<device_id>     → UPDATED: Broadcaster view
├── /auto_viewer/<session_id>  → NEW: Auto-connect viewer
├── /view_list                 → List of active broadcasts
├── /view/<session_id>         → Manual viewer with password
│
API Endpoints:
├── POST /verify_password/<session_id>  → NEW: Password validation
```

## Timeline: Session Creation to Broadcasting

```
T0:00s   User clicks "Start Broadcasting" on home page
T0:05s   Broadcast setup page loads (/brodcast_dets)
T0:10s   User enters "My Office" as room name
T0:15s   User clicks "Create Session"
T0:20s   CLIENT generates credentials locally:
         • SESSION ID: SESSION-A7K9M2Z1
         • PASSWORD: X4Q8J2P9
         • DEVICE ID: DEV-KL9N2Q4X
T0:25s   Credentials displayed with copy buttons
T0:30s   Links generated:
         • Auto: http://localhost/auto_viewer/SESSION-A7K9M2Z1?pwd=X4Q8J2P9
         • Manual: http://localhost/view_list?session=SESSION-A7K9M2Z1
T0:35s   User clicks "Share Your Screen Now"
T0:40s   Redirects to /broadcast/DEV-KL9N2Q4X
T0:45s   Browser requests screen capture permission
T0:50s   User grants permission
T0:55s   Screen capture begins
T1:00s   Socket.IO registers device with broadcaster credentials
T1:05s   Server stores: broadcast_sessions[DEV-KL9N2Q4X] = {...}
T1:10s   Broadcaster view displays active stream
T1:15s   Status: "Broadcast is LIVE and ready for connections"
         🔴 READY TO ACCEPT VIEWERS
```

