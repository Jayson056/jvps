# JVPS Render Deployment Guide

## ✅ Current Status
- **Service**: Live at https://jvps.onrender.com
- **Status**: Active and running
- **Python Version**: 3.13.4
- **Framework**: Flask + Flask-SocketIO + WebRTC

## 📋 Deployment Files

### Procfile
Specifies how Render should start the application:
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT "app:app"
```
- Uses **eventlet** worker class for async I/O (required for WebRTC/SocketIO)
- Single worker (`-w 1`) - Render free tier limitation
- Binds to dynamic PORT provided by Render

### render.yaml
Complete Render service configuration:
```yaml
services:
  - type: web
    name: jvps
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT "app:app"
    envVars:
      - PYTHON_VERSION: 3.13.4
      - FLASK_ENV: production
      - PYTHONUNBUFFERED: 1
```

### runtime.txt
Specifies Python version for Render:
```
python-3.13.4
```

### .renderignore
Excludes unnecessary files from deployment (reduces build size):
- Virtual environment files
- Documentation files
- Cache and build artifacts
- Reduces build time and deployment size

## 🔧 Environment Variables (Render Dashboard)

Set these in Render's dashboard under Environment Variables:

| Variable | Value | Purpose |
|----------|-------|---------|
| `FLASK_ENV` | `production` | Disables debug mode |
| `PYTHON_VERSION` | `3.13.4` | Python version |
| `PYTHONUNBUFFERED` | `1` | Real-time log output |
| `SECRET_KEY` | `[random-string]` | Flask session encryption |

## 📊 Application Architecture on Render

### What Works on Headless Server ✅
1. **WebRTC Video/Audio Streaming** - Peer-to-peer communication
2. **Socket.IO Signaling** - Connection relay and management
3. **Session Management** - Password verification and session tracking
4. **File Serving** - HTML templates, CSS, JavaScript
5. **REST APIs** - Broadcaster list, password verification

### What's Skipped on Headless Server ⏭️
1. **Desktop Control (Mouse/Keyboard)** - Requires X11 DISPLAY environment
   - Reason: Headless servers have no graphical display
   - Gracefully skipped with `[CONTROL_SKIPPED]` logs
   - Desktop control works on the broadcaster's local machine

## 🚀 Deployment Workflow

### Initial Deployment (Already Done)
```bash
# 1. Repository connected to Render
# 2. Branch: main
# 3. Auto-deploy on git push enabled
# 4. Build successful with all dependencies
# 5. Service deployed and live
```

### Redeployment After Code Changes
```bash
# 1. Make changes locally
# 2. Commit changes: git commit -m "..."
# 3. Push to GitHub: git push origin main
# 4. Render auto-detects and redeploys
# 5. Check logs in Render dashboard
```

## 📝 Log Locations

### Render Logs
- **Dashboard**: https://dashboard.render.com → Select "jvps" service → Logs tab
- **Real-time**: Live tail shows deployment and runtime logs
- Shows all HTTP requests, WebSocket connections, control inputs

### Local Logs
- **File**: `logs.txt` in project root
- **Contains**: All events logged during execution
- **Format**: `[TIMESTAMP] [EVENT_TYPE] Message`

## 🔐 Security Configuration

### Current Setup
- CORS enabled for all origins (`cors_allowed_origins="*"`)
- Password protection for broadcast sessions
- SSL/TLS provided by Render (HTTPS automatically)

### For Production Hardening
1. Set specific CORS origins in app.py
2. Configure more restrictive password validation
3. Add rate limiting for password attempts
4. Implement session timeout

## 📦 Dependencies

### Core Framework
- Flask 3.1.0 - Web server
- Flask-SocketIO 5.3.6 - WebSocket communication
- Gunicorn 23.0.0 - WSGI HTTP server
- Eventlet 0.40.4 - Async I/O library

### WebRTC/Media
- aiortc 1.14.0 - WebRTC implementation
- av 16.1.0 - Audio/video processing
- aioice 0.10.2 - ICE protocol

### Desktop (Not Used on Server)
- PyAutoGUI, PyGetWindow, PyScreeze, mss - Skipped on headless

All versions pinned in `requirements.txt` for reproducible builds.

## ✅ Health Checks

### Verify Service Status
```bash
# Check if service is responding
curl https://jvps.onrender.com/

# Expected response: HTML home page
```

### Monitor Real-Time Logs
- Render Dashboard → jvps service → Live tail
- Shows WebSocket connections, HTTP requests, errors

### Common Log Messages
- `[DEVICE_REGISTERED] BROADCASTER` - Broadcaster connected
- `[VIEWER_JOINING]` - Viewer connected
- `[SIGNAL_RELAY]` - WebRTC signal relayed
- `[CONTROL_SKIPPED]` - Control input skipped (expected on headless)

## 🛠️ Troubleshooting

### Build Failures
1. Check requirements.txt for version conflicts
2. Verify all dependencies are Render-compatible
3. Check runtime.txt for Python version support
4. View full build logs in Render dashboard

### Runtime Errors
1. Check Render live logs for error details
2. Verify environment variables are set correctly
3. Check Socket.IO and CORS configuration
4. Review logs.txt for application-level errors

### Connection Issues
1. Ensure HTTPS is working: https://jvps.onrender.com
2. Check firewall/CORS settings
3. Verify Socket.IO transport method (polling/websocket)
4. Check WebRTC signaling in browser console

## 📚 Resources

- Render Docs: https://render.com/docs
- Python on Render: https://render.com/docs/deploy-python
- SocketIO Deployment: https://python-socketio.readthedocs.io/
- Flask Deployment: https://flask.palletsprojects.com/deployment/

## 🎯 Next Steps

1. **Monitor Performance**
   - Watch for resource usage in Render dashboard
   - Upgrade tier if needed (free tier has limitations)

2. **Optimize for Production**
   - Set proper CORS origins instead of "*"
   - Configure session timeout and cleanup
   - Implement rate limiting

3. **Scale Up**
   - Upgrade from free to starter/standard tier
   - Add multiple workers for concurrency
   - Implement database for session persistence

4. **Add Features**
   - File transfer capability
   - Session recording
   - User authentication system
   - Analytics and monitoring
