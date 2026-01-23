# server/app.py
from flask import Flask, render_template, request, jsonify, session as flask_session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import secrets
import hashlib
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------------------------
# Logging and File Setup
# ---------------------------
LOG_FILE = Path(__file__).parent.parent / 'logs.txt'
PASSWORD_FILE = Path(__file__).parent.parent / 'password.txt'

def log_event(event_type, message):
    """Log events to logs.txt with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] [{event_type}] {message}\n"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message)
    print(f"[{event_type}] {message}")

def generate_password():
    """Generate an 8-character hex password"""
    return secrets.token_hex(4).upper()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def save_password_to_file(device_id, room_name, broadcaster_name, session_id, password):
    """Save broadcast credentials to password.txt"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    separator = "=" * 70
    
    credentials_text = f"""\n{separator}
BROADCAST SESSION CREATED
{separator}
Timestamp:        {timestamp}
Device ID:        {device_id}
Session ID:       {session_id}
Room Name:        {room_name}
Broadcaster Name: {broadcaster_name}
Password:         {password}
Password Hash:    {hash_password(password)}
{separator}\n"""
    
    with open(PASSWORD_FILE, 'a', encoding='utf-8') as f:
        f.write(credentials_text)
    
    log_event("PASSWORD_CREATED", f"Credentials saved - Room: {room_name}, Session: {session_id}")

# ---------------------------
# Device registry and sessions
# ---------------------------
devices = {}  # device_id -> {'role': 'broadcaster'/'viewer', 'sid': socket_id, 'approved': bool}
sessions = {}  # session_id -> {'broadcaster': device_id, 'viewers': [device_ids], 'password': str, 'room_name': str}
broadcast_sessions = {}  # device_id -> {'session_id': session_id, 'password': password, 'room_name': room_name, 'broadcaster_name': broadcaster_name}

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/brodcast_dets')
def brodview_new():
    """Broadcast setup page - create session with password"""
    return render_template('brodcast_dets.html')

@app.route('/api/create_session', methods=['POST'])
def api_create_session():
    """API endpoint to create a broadcast session with credentials"""
    data = request.json
    room_name = data.get('room_name', 'Untitled Room')
    broadcaster_name = data.get('broadcaster_name', 'Anonymous')
    
    # Generate credentials
    device_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    password = generate_password()
    
    # Save to password.txt
    save_password_to_file(device_id, room_name, broadcaster_name, session_id, password)
    
    # Store in broadcast_sessions
    broadcast_sessions[device_id] = {
        'session_id': session_id,
        'password': password,
        'room_name': room_name,
        'broadcaster_name': broadcaster_name,
        'created_at': datetime.now().isoformat()
    }
    
    # Log the creation
    log_event("SESSION_CREATED", f"Room: {room_name} | Broadcaster: {broadcaster_name} | Device: {device_id}")
    
    # Generate shareable links with production domain
    # Use jvps.onrender.com as the default domain for production
    production_domain = "http://jvps.onrender.com"
    
    # In development/local, use request.host_url; in production, use the domain above
    if request.host.startswith('localhost') or request.host.startswith('127.0.0.1'):
        base_url = request.host_url.rstrip('/')
    else:
        base_url = production_domain
    
    auto_viewer_link = f"{base_url}/auto_viewer/{session_id}?pwd={password}"
    manual_viewer_link = f"{base_url}/view/{session_id}"
    
    return jsonify({
        'success': True,
        'device_id': device_id,
        'session_id': session_id,
        'password': password,
        'room_name': room_name,
        'broadcaster_name': broadcaster_name,
        'auto_viewer_link': auto_viewer_link,
        'manual_viewer_link': manual_viewer_link,
        'broadcaster_url': f"{base_url}/broadcast/{device_id}"
    })

@app.route('/view_list')
def view_list():
    # Show available broadcasters
    broadcasters = [d_id for d_id, d in devices.items() if d['role'] == 'broadcaster']
    return render_template('view_list.html', broadcasters=broadcasters)

@app.route('/view/<session_id>')
def view_screen(session_id):
    # Viewer page for a given session
    if session_id not in sessions:
        return "Session not found", 404
    return render_template('view_screen.html', session_id=session_id)

@app.route('/broadcast/<device_id>')
def brodview_screen(device_id):
    # Broadcaster view - verify device exists
    if device_id not in devices:
        return "Device not found", 404
    
    # Get broadcast session info
    broadcast_info = broadcast_sessions.get(device_id, {})
    session_id = broadcast_info.get('session_id', 'UNKNOWN')
    
    return render_template('brodview_screen.html', device_id=device_id, session_id=session_id)

@app.route('/auto_viewer/<session_id>')
def auto_viewer(session_id):
    """Auto-viewer page - direct access with password in URL"""
    # Find the device with this session_id
    device_id = None
    password_from_url = request.args.get('pwd', '')
    
    for dev_id, broadcast_info in broadcast_sessions.items():
        if broadcast_info.get('session_id') == session_id:
            device_id = dev_id
            break
    
    if not device_id:
        return "Session not found", 404
    
    return render_template('auto_viewer.html', session_id=session_id, password=password_from_url)

@app.route('/verify_password/<session_id>', methods=['POST'])
def verify_password(session_id):
    """Verify the password for a broadcast session"""
    data = request.json
    password = data.get('password', '')
    
    # Find session by session_id
    for device_id, broadcast_info in broadcast_sessions.items():
        if broadcast_info.get('session_id') == session_id:
            if broadcast_info.get('password') == password:
                return jsonify({'success': True, 'device_id': device_id})
            else:
                return jsonify({'success': False, 'error': 'Invalid password'}), 401
    
    return jsonify({'success': False, 'error': 'Session not found'}), 404

# ---------------------------
# Socket.IO events
# ---------------------------

@socketio.on('register_device')
def register_device(data):
    """
    data = {
        'role': 'broadcaster' or 'viewer',
        'device_id': 'optional device_id',
        'session_id': 'optional session_id for broadcasters',
        'password': 'optional password for broadcasters',
        'room_name': 'optional room name',
        'broadcaster_name': 'optional broadcaster name'
    }
    """
    # Use provided device_id or generate a new one
    device_id = data.get('device_id') or str(uuid.uuid4())
    
    devices[device_id] = {'role': data['role'], 'sid': request.sid, 'approved': False}
    emit('device_registered', {'device_id': device_id})
    
    # If broadcaster, store session info
    if data['role'] == 'broadcaster':
        broadcast_sessions[device_id] = {
            'session_id': data.get('session_id', ''),
            'password': data.get('password', ''),
            'room_name': data.get('room_name', 'Untitled Room'),
            'broadcaster_name': data.get('broadcaster_name', 'Anonymous')
        }
        log_event("BROADCASTER_REGISTERED", f"Device: {device_id} | Room: {broadcast_sessions[device_id]['room_name']}")
    else:
        log_event("DEVICE_REGISTERED", f"Device: {device_id} | Role: {data['role']}")
    
    return device_id

@socketio.on('create_session')
def create_session(data):
    """
    data = {
        'device_id': broadcaster_id
    }
    """
    session_id = str(uuid.uuid4())
    sessions[session_id] = {'broadcaster': data['device_id'], 'viewers': []}
    emit('session_created', {'session_id': session_id})
    log_event("SESSION_CREATED", f"Session: {session_id} for broadcaster {data['device_id']}")
    return session_id

@socketio.on('join_session')
def join_session(data):
    """
    data = {
        'session_id': session_id,
        'device_id': viewer_id
    }
    """
    session_id = data['session_id']
    device_id = data['device_id']
    if session_id not in sessions:
        emit('error', {'message': 'Session not found'})
        log_event("VIEWER_JOIN_FAILED", f"Session not found: {session_id} | Viewer: {device_id}")
        return
    sessions[session_id]['viewers'].append(device_id)
    join_room(session_id)
    # Notify broadcaster for approval
    broadcaster_id = sessions[session_id]['broadcaster']
    emit('viewer_request', {'viewer_id': device_id}, room=devices[broadcaster_id]['sid'])
    log_event("VIEWER_JOIN_REQUEST", f"Session: {session_id} | Viewer: {device_id}")

@socketio.on('approve_viewer')
def approve_viewer(data):
    """
    data = {
        'session_id': session_id,
        'viewer_id': device_id,
        'approve': True/False
    }
    """
    session_id = data['session_id']
    viewer_id = data['viewer_id']
    approve = data['approve']
    if approve:
        devices[viewer_id]['approved'] = True
        emit('viewer_approved', {'approved': True}, room=devices[viewer_id]['sid'])
        log_event("VIEWER_APPROVED", f"Viewer: {viewer_id} approved for session {session_id}")
    else:
        sessions[session_id]['viewers'].remove(viewer_id)
        emit('viewer_approved', {'approved': False}, room=devices[viewer_id]['sid'])
        log_event("VIEWER_DENIED", f"Viewer: {viewer_id} denied for session {session_id}")

# ---------------------------
# WebRTC signaling
# ---------------------------
@socketio.on('signal')
def signal(data):
    """
    data = {
        'session_id': session_id,
        'from': device_id,
        'to': device_id,
        'signal': signaling_data
    }
    """
    target_sid = devices.get(data['to'], {}).get('sid')
    if target_sid:
        emit('signal', {'from': data['from'], 'signal': data['signal']}, room=target_sid)
        log_event("SIGNAL_SENT", f"From: {data['from']} | To: {data['to']}")

# ---------------------------
# Viewer control
# ---------------------------
@socketio.on('control_input')
def control_input(data):
    """
    data = {
        'session_id': session_id,
        'viewer_id': device_id,
        'action': {'type': 'mouse'/'keyboard', 'data': ...}
    }
    """
    session_id = data['session_id']
    broadcaster_id = sessions.get(session_id, {}).get('broadcaster')
    if broadcaster_id:
        emit('control_input', data['action'], room=devices[broadcaster_id]['sid'])
        log_event("CONTROL_INPUT", f"Session: {session_id} | Action: {data['action'].get('type', 'unknown')}")

# ---------------------------
# Broadcaster Agent Registration
# ---------------------------
@socketio.on('register_broadcaster_agent')
def register_broadcaster_agent(data):
    """
    Register a broadcaster agent running on local machine
    data = {
        'session_id': session_id,
        'device_id': device_id,
        'timestamp': datetime
    }
    """
    session_id = data.get('session_id')
    device_id = data.get('device_id')
    timestamp = data.get('timestamp')
    
    # Register the broadcaster agent
    devices[device_id] = {
        'role': 'broadcaster_agent',
        'sid': request.sid,
        'approved': True,
        'registered_at': timestamp
    }
    
    # Link to session
    if session_id in sessions:
        sessions[session_id]['broadcaster_agent_id'] = device_id
        emit('broadcaster_ready', {
            'device_id': device_id,
            'session_id': session_id
        })
        log_event("AGENT_REGISTERED", f"Agent: {device_id} | Session: {session_id}")
    else:
        log_event("AGENT_REGISTRATION_FAILED", f"Agent: {device_id} | Session {session_id} not found")

# ---------------------------
# Disconnect
# ---------------------------
@socketio.on('disconnect')
def disconnect():
    sid = request.sid
    for device_id, device in list(devices.items()):
        if device['sid'] == sid:
            log_event("DEVICE_DISCONNECTED", f"Device: {device_id} | Role: {device['role']}")
            # Remove from sessions
            for s_id, s_data in sessions.items():
                if device_id == s_data['broadcaster']:
                    # End session
                    emit('session_ended', room=s_id)
                    log_event("SESSION_ENDED", f"Session: {s_id} (broadcaster disconnected)")
                    del sessions[s_id]
                elif device_id in s_data['viewers']:
                    s_data['viewers'].remove(device_id)
                    log_event("VIEWER_LEFT", f"Viewer: {device_id} left session {s_id}")
            del devices[device_id]

# ---------------------------
# Main
# ---------------------------
if __name__ == '__main__':
    log_event("STARTUP", "OmniStream Pro server starting on 0.0.0.0:58247")
    socketio.run(app, host='0.0.0.0', port=58247, debug=True)
