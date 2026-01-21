# server/app.py
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------------------------
# Device registry and sessions
# ---------------------------
devices = {}  # device_id -> {'role': 'broadcaster'/'viewer', 'sid': socket_id, 'approved': bool}
sessions = {}  # session_id -> {'broadcaster': device_id, 'viewers': [device_ids]}

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def home():
    return render_template('home.html')

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
    # Broadcaster view
    if device_id not in devices:
        return "Device not found", 404
    return render_template('brodview_screen.html', device_id=device_id)

# ---------------------------
# Socket.IO events
# ---------------------------

@socketio.on('register_device')
def register_device(data):
    """
    data = {
        'role': 'broadcaster' or 'viewer',
        'name': 'optional name'
    }
    """
    device_id = str(uuid.uuid4())
    devices[device_id] = {'role': data['role'], 'sid': request.sid, 'approved': False}
    emit('device_registered', {'device_id': device_id})
    print(f"[INFO] Device registered: {device_id} as {data['role']}")
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
    print(f"[INFO] Session created: {session_id} for broadcaster {data['device_id']}")
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
        return
    sessions[session_id]['viewers'].append(device_id)
    join_room(session_id)
    # Notify broadcaster for approval
    broadcaster_id = sessions[session_id]['broadcaster']
    emit('viewer_request', {'viewer_id': device_id}, room=devices[broadcaster_id]['sid'])
    print(f"[INFO] Viewer {device_id} requested to join session {session_id}")

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
        print(f"[INFO] Viewer {viewer_id} approved for session {session_id}")
    else:
        sessions[session_id]['viewers'].remove(viewer_id)
        emit('viewer_approved', {'approved': False}, room=devices[viewer_id]['sid'])
        print(f"[INFO] Viewer {viewer_id} denied for session {session_id}")

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

# ---------------------------
# Disconnect
# ---------------------------
@socketio.on('disconnect')
def disconnect():
    sid = request.sid
    for device_id, device in list(devices.items()):
        if device['sid'] == sid:
            print(f"[INFO] Device disconnected: {device_id}")
            # Remove from sessions
            for s_id, s_data in sessions.items():
                if device_id == s_data['broadcaster']:
                    # End session
                    emit('session_ended', room=s_id)
                    del sessions[s_id]
                elif device_id in s_data['viewers']:
                    s_data['viewers'].remove(device_id)
            del devices[device_id]

# ---------------------------
# Main
# ---------------------------
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
