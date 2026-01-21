// static/js/webrtc_viewer.js

const socket = io();  // Connect to Flask Socket.IO
let pc = null;         // RTCPeerConnection
let deviceId = null;    // Viewer device ID
let sessionId = window.SESSION_ID || null; // Current session from template
let broadcasterId = null; // Will be set during signaling
let remoteVideo = document.getElementById('remoteVideo');

// Control States
let mouseEnabled = true;
let kbdEnabled = true;

// ---------------------------
// 1. Socket.IO Registration
// ---------------------------
socket.on('connect', () => {
    console.log("[INFO] Connected to server");
    socket.emit('register_device', { role: 'viewer', device_id: null });
});

socket.on('device_registered', (data) => {
    deviceId = data.device_id;
    console.log("[INFO] Viewer registered with ID:", deviceId);

    if (sessionId) {
        console.log("[INFO] Joining session:", sessionId);
        socket.emit('join_session', { session_id: sessionId, device_id: deviceId });
    }
});

// The server tells us we are approved to receive the stream
socket.on('viewer_approved', (data) => {
    if (data.approved) {
        console.log("[INFO] Approved! Waiting for offer from broadcaster...");
        startWebRTC();
    } else {
        alert("Access denied by broadcaster.");
    }
});

// ---------------------------
// 2. WebRTC Setup
// ---------------------------
function startWebRTC() {
    pc = new RTCPeerConnection({
        iceServers: [
            { urls: "stun:stun.l.google.com:19302" },
            { urls: "stun:stun1.l.google.com:19302" }
        ]
    });

    // Handle incoming video stream
    pc.ontrack = event => {
        console.log("[INFO] Remote stream received");
        if (remoteVideo.srcObject !== event.streams[0]) {
            remoteVideo.srcObject = event.streams[0];
            remoteVideo.play();
        }
    };

    // Send network candidates back to broadcaster
    pc.onicecandidate = event => {
        if (event.candidate && broadcasterId) {
            socket.emit('signal', {
                from: deviceId,
                to: broadcasterId,
                signal: { candidate: event.candidate }
            });
        }
    };

    pc.onconnectionstatechange = () => {
        console.log(`[INFO] WebRTC State: ${pc.connectionState}`);
    };
}

// ---------------------------
// 3. Signaling Handler
// ---------------------------
socket.on('signal', async (data) => {
    if (data.signal.sdp) {
        const desc = new RTCSessionDescription(data.signal.sdp);

        if (desc.type === 'offer') {
            broadcasterId = data.from;
            console.log("[INFO] Offer received from:", broadcasterId);

            if (!pc) startWebRTC();

            await pc.setRemoteDescription(desc);
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);

            console.log("[INFO] Sending answer to broadcaster");
            socket.emit('signal', {
                from: deviceId,
                to: broadcasterId,
                signal: { sdp: pc.localDescription }
            });
        }
    } else if (data.signal.candidate) {
        try {
            if (pc) {
                await pc.addIceCandidate(new RTCIceCandidate(data.signal.candidate));
                console.log("[INFO] ICE candidate applied");
            }
        } catch (err) {
            console.error("[ERROR] Candidate error:", err);
        }
    }
});

// ---------------------------
// 4. Remote Control Logic
// ---------------------------
function sendControlInput(action) {
    if (!sessionId) return;
    socket.emit('control_input', {
        session_id: sessionId,
        action: action
    });
}

// Optimized Mouse listener with Coordinate Scaling
remoteVideo.addEventListener('mousemove', e => {
    if (!mouseEnabled) return;
    const rect = remoteVideo.getBoundingClientRect();

    // Scale coordinates to actual broadcaster video resolution
    const x = Math.floor((e.clientX - rect.left) * (remoteVideo.videoWidth / rect.width));
    const y = Math.floor((e.clientY - rect.top) * (remoteVideo.videoHeight / rect.height));

    if (!isNaN(x) && !isNaN(y)) {
        sendControlInput({ type: 'mouse', data: { x, y, move: true } });
    }
});

remoteVideo.addEventListener('click', e => {
    if (!mouseEnabled) return;
    const rect = remoteVideo.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) * (remoteVideo.videoWidth / rect.width));
    const y = Math.floor((e.clientY - rect.top) * (remoteVideo.videoHeight / rect.height));

    sendControlInput({
        type: 'mouse',
        data: { x, y, click: true, button: 'left' }
    });
});

// Keyboard listeners
window.addEventListener('keydown', e => {
    if (!kbdEnabled) return;
    sendControlInput({ type: 'keyboard', data: { key: e.key, action: 'down' } });
});

window.addEventListener('keyup', e => {
    if (!kbdEnabled) return;
    sendControlInput({ type: 'keyboard', data: { key: e.key, action: 'up' } });
});

// ---------------------------
// 5. UI Controls (Buttons)
// ---------------------------

// Fullscreen
const btnFull = document.getElementById('btnFull');
if (btnFull) {
    btnFull.addEventListener('click', () => {
        if (remoteVideo.requestFullscreen) {
            remoteVideo.requestFullscreen();
        } else if (remoteVideo.webkitRequestFullscreen) { /* Safari */
            remoteVideo.webkitRequestFullscreen();
        }
    });
}

// Rotate
const btnRotate = document.getElementById('btnRotate');
if (btnRotate) {
    btnRotate.addEventListener('click', () => {
        remoteVideo.classList.toggle('rotated');
    });
}

// Toggle Mouse
const toggleMouseBtn = document.getElementById('toggleMouse');
if (toggleMouseBtn) {
    toggleMouseBtn.addEventListener('click', () => {
        mouseEnabled = !mouseEnabled;
        toggleMouseBtn.innerText = `Mouse: ${mouseEnabled ? 'ON' : 'OFF'}`;
        toggleMouseBtn.classList.toggle('btn-primary');
        toggleMouseBtn.classList.toggle('btn-warning');
    });
}

// Toggle Keyboard
const toggleKbdBtn = document.getElementById('toggleKbd');
if (toggleKbdBtn) {
    toggleKbdBtn.addEventListener('click', () => {
        kbdEnabled = !kbdEnabled;
        toggleKbdBtn.innerText = `Kbd: ${kbdEnabled ? 'ON' : 'OFF'}`;
        toggleKbdBtn.classList.toggle('btn-primary');
        toggleKbdBtn.classList.toggle('btn-warning');
    });
}