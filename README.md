# JVPS Desktop Remote

**Link**
# https://jvps.onrender.com/

**Remote Desktop Control & Screen Sharing Solution**

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python app.py
```

The application will:
- Start the Flask server on `http://localhost:5000`
- Auto-start the broadcaster agent in background
- Display prompt for session credentials

### 3. Access the Application
- **Home**: http://localhost:5000/
- **Broadcast Setup**: http://localhost:5000/brodcast_dets
- **View List**: http://localhost:5000/view_list

## Features

✅ **Remote Desktop Control**
- Mouse movement & clicks
- Keyboard input
- Real-time interaction

✅ **Screen Sharing**
- WebRTC video streaming
- Low-latency transmission
- Secure password protection

✅ **Multi-User Support**
- Multiple viewers per broadcaster
- Session management
- Device authentication

## Architecture

```
Viewer (Browser)
     ↓ (WebSocket)
Render/Local Server (Relay)
     ↓ (Socket.IO)
Broadcaster Agent (Desktop Control)
```

- **Server**: Relays signals between viewer and broadcaster
- **Agent**: Executes screen capture and mouse/keyboard controls
- **Viewer**: Web-based control interface

## Security

- Password-protected sessions
- Session IDs for authentication
- No stored credentials on disk
- Secure WebSocket communication

## Files Structure

```
├── app.py                    # Main Flask application
├── agent/
│   └── broadcaster_agent.py  # Desktop control agent
├── templates/                # HTML templates
├── static/
│   ├── css/                 # Stylesheets
│   └── js/                  # Client-side scripts
├── requirements.txt          # Python dependencies
└── logs.txt                 # Activity logs (auto-generated)
```

## Troubleshooting

**No screen sharing after clicking OK?**
- Agent needs to be running (auto-starts with app.py)
- Check browser console for errors
- Verify agent is connected (check logs.txt)

**Permission denied on Windows?**
- Grant screen capture permissions when prompted
- Run terminal as Administrator if needed

**Cannot connect to localhost?**
- Ensure port 5000 is not in use
- Check firewall settings
- Try `http://localhost:5000` in browser

## Deployment

For cloud deployment on Render:
- Server runs on Render (relay only)
- Agent runs locally on broadcaster's machine
- No GUI packages needed on cloud

## Support

For issues or questions, check the logs.txt file for detailed diagnostic information.
