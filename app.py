# server/app.py
from flask import Flask, render_template, request, jsonify, session as flask_session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import threading
import time
import secrets
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ---------------------------
# LOGGING SETUP
# ---------------------------
LOG_FILE = 'logs.txt'

def log_event(event_type, message):
    """Log events to logs.txt file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] [{event_type}] {message}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_message)
    print(log_message.strip())

# ---------------------------
# Device registry and sessions
# ---------------------------
devices = {}   # device_id -> {'role': 'broadcaster'/'viewer', 'sid': socket_id}
sessions = {}  # session_id -> {'broadcaster': device_id, 'viewers': [], 'auto_viewer_id': None}
active_broadcasters = set()  # Track active broadcaster device IDs
broadcast_sessions = {}  # device_id -> {'session_id': session_id, 'password': password, 'room_name': room_name, 'broadcaster_name': broadcaster_name, 'password_file': path}

log_event('STARTUP', 'Application started')

# PyAutoGUI Configuration (lazy loaded in execute_control)
MOUSE_SPEED = 0.1  # seconds for smooth movement

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def generate_password():
    """Generate a secure 8-character password"""
    return secrets.token_hex(4).upper()

def hash_password(password):
    """Generate SHA256 hash of password"""
    return hashlib.sha256(password.encode()).hexdigest()

def save_password_to_file(device_id, room_name, broadcaster_name, session_id, password):
    """Save password and session info to password.txt file"""
    password_file = 'password.txt'
    password_hash = hash_password(password)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content = f"""
================================================================================
BROADCAST SESSION CREATED
================================================================================
Timestamp:          {timestamp}
Device ID:          {device_id}
Session ID:         {session_id}
Room Name:          {room_name}
Broadcaster Name:   {broadcaster_name or 'Anonymous'}
Password:           {password}
Password Hash:      {password_hash}

Auto-Viewer Link:   http://localhost:5000/auto_viewer/{session_id}?pwd={password}
Manual View Link:   http://localhost:5000/view_list?session={session_id}

================================================================================
NOTE: Keep this password secure. Share the links with authorized viewers only.
================================================================================

"""
    
    with open(password_file, 'a') as f:
        f.write(content)
    
    log_event('PASSWORD_GENERATED', f'Device: {device_id}, Room: {room_name}')
    return password_file

def execute_control(action):
    """
    Executes incoming control commands from the remote viewer.
    action: dict with keys:
        - type: 'mouse' or 'keyboard'
        - data: dict containing coordinates or key names
    
    Note: Desktop control only works on systems with a display (DISPLAY env var set).
    On headless servers (Render, etc.), this will be skipped with a log message.
    """
    try:
        # Lazy import pyautogui - only import when actually controlling the desktop
        # This prevents DISPLAY environment errors on headless servers
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
        except (KeyError, ImportError) as import_err:
            # KeyError: DISPLAY environment variable not set (headless server)
            # ImportError: pyautogui or its dependencies failed to load
            is_headless = 'DISPLAY' in str(import_err) or isinstance(import_err, KeyError)
            if is_headless:
                log_event('CONTROL_SKIPPED', f'Desktop control skipped - running on headless server (no DISPLAY)')
                return  # Silently skip on headless servers
            else:
                raise  # Re-raise other import errors
        
        if action['type'] == 'mouse':
            data = action['data']
            x, y = data.get('x'), data.get('y')
            
            if x is not None and y is not None:
                # Handle Movement
                if data.get('move'):
                    pyautogui.moveTo(x, y, duration=MOUSE_SPEED)
                
                # Handle Clicks
                if data.get('click'):
                    button = data.get('button', 'left')
                    pyautogui.click(x, y, button=button)

        elif action['type'] == 'keyboard':
            data = action['data']
            key = data.get('key')
            action_type = data.get('action', 'press')

            # Standardize key names
            key = key.lower() if len(key) > 1 else key

            if action_type == 'press':
                pyautogui.press(key)
            elif action_type == 'down':
                pyautogui.keyDown(key)
            elif action_type == 'up':
                pyautogui.keyUp(key)

    except Exception as e:
        log_event('CONTROL_ERROR', f'Failed to execute control: {str(e)}')

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def home():
    log_event('USER_ACTION', 'User accessed home page')
    return render_template('home.html')

@app.route('/brodcast_dets')
def brodcast_dets():
    """Broadcast setup page - NEW SECURITY LAYER"""
    log_event('USER_ACTION', 'User accessed broadcast setup page')
    return render_template('brodcast_dets.html')

@app.route('/view_list')
def view_list():
    # Only show sessions that actually have a broadcaster registered
    active_sessions = [s_id for s_id, s in sessions.items() if s['broadcaster'] in devices]
    log_event('USER_ACTION', f'User accessed view list. Active sessions: {len(active_sessions)}')
    return render_template('view_list.html', broadcasters=active_sessions)

@app.route('/api/broadcasters')
def get_broadcasters():
    """API endpoint for fetching active broadcasters with details (for auto-refresh)"""
    active_sessions = [s_id for s_id, s in sessions.items() if s['broadcaster'] in devices]
    
    # Build detailed broadcaster list
    broadcasters_detail = []
    for session_id in active_sessions:
        broadcaster_id = sessions[session_id]['broadcaster']
        broadcast_info = broadcast_sessions.get(broadcaster_id, {})
        
        broadcasters_detail.append({
            'session_id': session_id,
            'device_id': broadcaster_id,
            'room_name': broadcast_info.get('room_name', 'Untitled Room'),
            'broadcaster_name': broadcast_info.get('broadcaster_name', 'Anonymous'),
            'viewer_count': len(sessions[session_id]['viewers'])
        })
    
    return jsonify({'broadcasters': broadcasters_detail})

@app.route('/api/create_session', methods=['POST'])
def create_session():
    """API endpoint for creating a broadcast session with credentials"""
    data = request.json
    room_name = data.get('room_name', 'Untitled Room')
    broadcaster_name = data.get('broadcaster_name', '')
    
    # Generate credentials
    device_id = 'DEV-' + secrets.token_hex(4).upper()
    session_id = 'SESSION-' + secrets.token_hex(12).upper()
    password = generate_password()
    
    # Save to password file
    password_file = save_password_to_file(device_id, room_name, broadcaster_name, session_id, password)
    
    # Store in broadcast_sessions
    broadcast_sessions[device_id] = {
        'session_id': session_id,
        'password': password,
        'room_name': room_name,
        'broadcaster_name': broadcaster_name,
        'password_file': password_file
    }
    
    # Create session
    sessions[session_id] = {
        'broadcaster': device_id,
        'viewers': [],
        'auto_viewer_id': None
    }
    
    # Pre-register device
    devices[device_id] = {'role': 'broadcaster', 'sid': None}
    active_broadcasters.add(device_id)
    
    log_event('SESSION_CREATED', f'Room: {room_name}, Device: {device_id}, Session: {session_id}')
    
    # Generate shareable links
    base_url = request.host_url.rstrip('/')
    auto_viewer_link = f"{base_url}/auto_viewer/{session_id}?pwd={password}"
    manual_viewer_link = f"{base_url}/view/{session_id}"
    broadcaster_url = f"{base_url}/broadcast/{device_id}"
    
    return jsonify({
        'success': True,
        'device_id': device_id,
        'session_id': session_id,
        'password': password,
        'room_name': room_name,
        'broadcaster_name': broadcaster_name,
        'auto_viewer_link': auto_viewer_link,
        'manual_viewer_link': manual_viewer_link,
        'broadcaster_url': broadcaster_url
    })

@app.route('/broadcast/<device_id>')
def brodview_screen(device_id):
    """Broadcaster view - UPDATED to show session info"""
    if device_id not in devices:
        log_event('ERROR', f'Unknown device accessed broadcast view: {device_id}')
        return "Device not found", 404
    
    # Get broadcast session info
    broadcast_info = broadcast_sessions.get(device_id, {})
    session_id = broadcast_info.get('session_id', 'UNKNOWN')
    password = broadcast_info.get('password', 'UNKNOWN')
    room_name = broadcast_info.get('room_name', 'Untitled Room')
    
    log_event('USER_ACTION', f'User accessing broadcaster view. Device: {device_id}, Room: {room_name}')
    
    return render_template('brodview_screen.html', 
                         device_id=device_id, 
                         session_id=session_id,
                         password=password,
                         room_name=room_name)

@app.route('/broadcast/new')
def brodview_new():
    """ DEPRECATED: Use /brodcast_dets instead """
    log_event('DEPRECATED', 'Old /broadcast/new route accessed. Redirecting to /brodcast_dets')
    return redirect(url_for('brodcast_dets'))

@app.route('/view/<session_id>')
def view_screen(session_id):
    if session_id not in sessions:
        log_event('ERROR', f'Session not found: {session_id}')
        return redirect(url_for('view_list'))
    
    # Check if password is provided in query parameter or session
    password_param = request.args.get('pwd', '')
    session_pass = flask_session.get(f'verified_{session_id}')
    
    # Find broadcaster and get stored password
    broadcaster_id = sessions[session_id]['broadcaster']
    stored_password = broadcast_sessions.get(broadcaster_id, {}).get('password', '')
    
    # If password is provided in URL, verify it
    if password_param:
        if password_param == stored_password:
            flask_session[f'verified_{session_id}'] = True
            log_event('USER_ACTION', f'User verified password for session: {session_id}')
            return render_template('view_screen.html', session_id=session_id)
        else:
            log_event('SECURITY', f'Invalid password attempt for session: {session_id}')
            return redirect(url_for('view_password', session_id=session_id) + '?error=1')
    
    # If already verified in session, allow access
    if session_pass:
        log_event('USER_ACTION', f'User accessing view screen for session: {session_id}')
        return render_template('view_screen.html', session_id=session_id)
    
    # Otherwise, redirect to password entry
    log_event('USER_ACTION', f'User redirected to password entry for session: {session_id}')
    return redirect(url_for('view_password', session_id=session_id))

@app.route('/view/<session_id>/password', endpoint='view_password')
def view_password(session_id):
    """Password entry page for viewers"""
    if session_id not in sessions:
        log_event('ERROR', f'Password page: Session not found: {session_id}')
        return redirect(url_for('view_list'))
    
    # Get room name from broadcast_sessions
    broadcaster_id = sessions[session_id]['broadcaster']
    room_name = broadcast_sessions.get(broadcaster_id, {}).get('room_name', 'Broadcast')
    error = request.args.get('error', '')
    
    log_event('USER_ACTION', f'User viewing password entry page for session: {session_id}')
    return render_template('view_password.html', session_id=session_id, room_name=room_name, error=error)

@app.route('/api/verify_password/<session_id>', methods=['POST'])
def verify_password_api(session_id):
    """API endpoint to verify password for a session"""
    if session_id not in sessions:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    data = request.json
    password = data.get('password', '')
    
    # Get stored password
    broadcaster_id = sessions[session_id]['broadcaster']
    stored_password = broadcast_sessions.get(broadcaster_id, {}).get('password', '')
    
    if password == stored_password:
        flask_session[f'verified_{session_id}'] = True
        log_event('SECURITY', f'Viewer successfully verified password for session: {session_id}')
        return jsonify({'success': True, 'redirect': url_for('view_screen', session_id=session_id)})
    else:
        log_event('SECURITY', f'Failed password attempt for session: {session_id}')
        return jsonify({'success': False, 'error': 'Invalid password'}), 401

@app.route('/auto_viewer/<session_id>')
def auto_viewer(session_id):
    """Auto-connect viewer to broadcaster (no manual approval needed)"""
    if session_id not in sessions:
        log_event('ERROR', f'Auto-viewer: Session not found: {session_id}')
        return "Session not found", 404
    log_event('USER_ACTION', f'User accessing auto-viewer for session: {session_id}')
    return render_template('auto_viewer.html', session_id=session_id)

# ---------------------------
# Socket.IO events
# ---------------------------

@socketio.on('register_device')
def register_device(data):
    # Fix: Use the ID sent by the browser (from the URL/Template) 
    # instead of generating a new one every time
    device_id = data.get('device_id') or str(uuid.uuid4())
    role = data.get('role', 'viewer')
    
    devices[device_id] = {
        'role': role,
        'sid': request.sid
    }
    
    # Get broadcast info if available
    broadcast_info = broadcast_sessions.get(device_id, {})
    room_name = broadcast_info.get('room_name', 'Unknown')
    
    emit('device_registered', {'device_id': device_id})
    log_event('DEVICE_REGISTERED', f'{role.upper()}: {device_id}, Room: {room_name}')

@socketio.on('join_session')
def join_session(data):
    session_id = data.get('session_id')
    viewer_id = data.get('device_id')
    auto_mode = data.get('auto_approve', False)
    
    log_event('VIEWER_JOINING', f'Viewer: {viewer_id}, Session: {session_id}, Auto-mode: {auto_mode}')
    
    if session_id in sessions:
        if viewer_id not in sessions[session_id]['viewers']:
            sessions[session_id]['viewers'].append(viewer_id)
        
        join_room(session_id)
        
        # Notify the broadcaster that a viewer is ready
        broadcaster_id = sessions[session_id]['broadcaster']
        if broadcaster_id in devices:
            target_sid = devices[broadcaster_id]['sid']
            emit('viewer_request', {'viewer_id': viewer_id}, to=target_sid)
            log_event('VIEWER_REQUEST', f'Viewer {viewer_id} requested access to session {session_id}')
            
            # Auto-approve if this is auto-mode
            if auto_mode and viewer_id in devices:
                emit('viewer_approved', {'approved': True}, to=devices[viewer_id]['sid'])
                log_event('VIEWER_APPROVED', f'Viewer {viewer_id} auto-approved for session {session_id}')
    else:
        log_event('ERROR', f'Session not found: {session_id}')
        emit('error', {'message': 'Session not found'})

@socketio.on('approve_viewer')
def approve_viewer(data):
    viewer_id = data.get('viewer_id')
    log_event('VIEWER_APPROVED', f'Broadcaster approved viewer: {viewer_id}')
    if viewer_id in devices:
        emit('viewer_approved', {'approved': True}, to=devices[viewer_id]['sid'])

# ---------------------------
# WebRTC signaling (The Bridge)
# ---------------------------
@socketio.on('signal')
def handle_signal(data):
    """
    Relays SDP and ICE candidates between Broadcaster and Viewer
    data: { 'to': target_id, 'from': my_id, 'signal': {...} }
    """
    target_id = data.get('to')
    if target_id in devices:
        target_sid = devices[target_id]['sid']
        log_event('SIGNAL_RELAY', f'Signal relayed from {data.get("from")} to {target_id}')
        emit('signal', data, to=target_sid)

# ---------------------------
# Viewer control (Mouse/Keyboard)
# ---------------------------
@socketio.on('control_input')
def control_input(data):
    session_id = data.get('session_id')
    broadcaster_id = sessions.get(session_id, {}).get('broadcaster')
    
    if not broadcaster_id:
        log_event('ERROR', f'No broadcaster found for session {session_id}')
        return
    
    if broadcaster_id not in devices:
        log_event('ERROR', f'Broadcaster {broadcaster_id} not registered in devices')
        return
    
    target_sid = devices[broadcaster_id]['sid']
    if not target_sid:
        log_event('ERROR', f'Broadcaster {broadcaster_id} has no SID assigned')
        return
    
    log_event('CONTROL_INPUT', f'Control from session {session_id}: {data.get("action", {}).get("type", "unknown")}')
    
    # Execute locally via PyAutoGUI (no need to wait for agent)
    execute_control(data['action'])

# ---------------------------
# Disconnect Handling
# ---------------------------
@socketio.on('disconnect')
def disconnect():
    sid = request.sid
    disconnected_id = None
    
    # Find which device disconnected
    for d_id, d_data in list(devices.items()):
        if d_data['sid'] == sid:
            disconnected_id = d_id
            del devices[d_id]
            break
            
    if disconnected_id:
        log_event('DEVICE_DISCONNECTED', f'Device: {disconnected_id}')
        
        # Clean up sessions associated with this broadcaster
        for s_id, s_data in list(sessions.items()):
            if s_data['broadcaster'] == disconnected_id:
                emit('session_ended', room=s_id)
                del sessions[s_id]
                active_broadcasters.discard(disconnected_id)
                log_event('SESSION_ENDED', f'Session: {s_id}')

# ---------------------------
# Latency Tracking
# ---------------------------
@socketio.on('ping_request')
def handle_ping(data):
    emit('pong_response', data)

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    log_event('STARTUP', 'Starting JVPS Desktop Remote server...')
    print("[INFO] Starting JVPS Desktop Remote server...")
    print("[INFO] Navigate to http://localhost:5000/ to start")
    print("[INFO] Logs are being saved to logs.txt")
    
    # Get port from environment variable or default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Run socketio with gunicorn in production, debug mode in development
    socketio.run(app, host="0.0.0.0", port=port, debug=debug_mode)