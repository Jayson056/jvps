# server/app.py
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ---------------------------
# Device registry and sessions
# ---------------------------
devices = {}   # device_id -> {'role': 'broadcaster'/'viewer', 'sid': socket_id}
sessions = {}  # session_id -> {'broadcaster': device_id, 'viewers': []}

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/view_list')
def view_list():
    # Only show sessions that actually have a broadcaster registered
    active_sessions = [s_id for s_id, s in sessions.items() if s['broadcaster'] in devices]
    return render_template('view_list.html', broadcasters=active_sessions)

@app.route('/broadcast/new')
def brodview_new():
    """ Create a session based on a new broadcaster ID """
    broadcaster_id = str(uuid.uuid4())
    session_id = broadcaster_id # Simplification: Session ID = Broadcaster ID
    
    sessions[session_id] = {'broadcaster': broadcaster_id, 'viewers': []}
    
    # Pre-register the device role (SID will be added on socket connect)
    devices[broadcaster_id] = {'role': 'broadcaster', 'sid': None}
    
    print(f"[INFO] New session created: {session_id}")
    return render_template('brodview_screen.html', device_id=broadcaster_id, session_id=session_id)

@app.route('/view/<session_id>')
def view_screen(session_id):
    if session_id not in sessions:
        return "Session not found", 404
    return render_template('view_screen.html', session_id=session_id)

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
    
    emit('device_registered', {'device_id': device_id})
    print(f"[INFO] {role.capitalize()} registered with ID: {device_id}")

@socketio.on('join_session')
def join_session(data):
    session_id = data.get('session_id')
    viewer_id = data.get('device_id')
    
    if session_id in sessions:
        if viewer_id not in sessions[session_id]['viewers']:
            sessions[session_id]['viewers'].append(viewer_id)
        
        join_room(session_id)
        
        # Notify the broadcaster that a viewer is ready
        broadcaster_id = sessions[session_id]['broadcaster']
        if broadcaster_id in devices:
            target_sid = devices[broadcaster_id]['sid']
            emit('viewer_request', {'viewer_id': viewer_id}, room=target_sid)
            print(f"[INFO] Viewer {viewer_id} joined session {session_id}")
    else:
        emit('error', {'message': 'Session not found'})

@socketio.on('approve_viewer')
def approve_viewer(data):
    viewer_id = data.get('viewer_id')
    if viewer_id in devices:
        emit('viewer_approved', {'approved': True}, room=devices[viewer_id]['sid'])

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
        emit('signal', data, room=target_sid)

# ---------------------------
# Viewer control (Mouse/Keyboard)
# ---------------------------
@socketio.on('control_input')
def control_input(data):
    session_id = data.get('session_id')
    broadcaster_id = sessions.get(session_id, {}).get('broadcaster')
    if broadcaster_id in devices:
        emit('control_input', data['action'], room=devices[broadcaster_id]['sid'])

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
        print(f"[INFO] Device disconnected: {disconnected_id}")
        # Clean up sessions associated with this broadcaster
        for s_id, s_data in list(sessions.items()):
            if s_data['broadcaster'] == disconnected_id:
                emit('session_ended', room=s_id)
                del sessions[s_id]
                print(f"[INFO] Session {s_id} ended.")

if __name__ == "__main__":
    print("[INFO] Starting OmniStream Pro server...")
    socketio.run(app, host="0.0.0.0", port=58247, debug=True)