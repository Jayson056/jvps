// static/js/webrtc_viewer.js

console.log('[WebRTC] Viewer script loading...');
console.log('[WebRTC] SESSION_ID:', window.SESSION_ID);

// Ensure video element exists
let remoteVideo = document.getElementById('remoteVideo');
if (!remoteVideo) {
    console.error('[ERROR] remoteVideo element not found!');
    throw new Error('Video element not found');
}

console.log('[WebRTC] Video element found:', remoteVideo);

const socket = io();  // Connect to Flask Socket.IO
let pc = null;         // RTCPeerConnection
let deviceId = null;    // Viewer device ID
let sessionId = window.SESSION_ID || null; // Current session from template
let broadcasterId = null; // Will be set during signaling

// Control States
let mouseEnabled = true;
let kbdEnabled = true;

console.log('[WebRTC] Initializing Socket.IO connection...');

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

// Helper function to calculate video display area accounting for aspect ratio
function getVideoDisplayArea() {
    if (!remoteVideo.videoWidth || !remoteVideo.videoHeight) {
        return null;
    }
    
    const rect = remoteVideo.getBoundingClientRect();
    const containerAspect = rect.width / rect.height;
    const videoAspect = remoteVideo.videoWidth / remoteVideo.videoHeight;
    
    let displayWidth, displayHeight, offsetX = 0, offsetY = 0;
    
    if (videoAspect > containerAspect) {
        // Video is wider than container (letterbox on top/bottom)
        displayWidth = rect.width;
        displayHeight = rect.width / videoAspect;
        offsetY = (rect.height - displayHeight) / 2;
    } else {
        // Video is taller than container (pillarbox on sides)
        displayHeight = rect.height;
        displayWidth = rect.height * videoAspect;
        offsetX = (rect.width - displayWidth) / 2;
    }
    
    return { displayWidth, displayHeight, offsetX, offsetY, containerRect: rect };
}

// Optimized Mouse listener with Aspect Ratio Aware Coordinate Scaling
remoteVideo.addEventListener('mousemove', e => {
    if (!mouseEnabled || !remoteVideo.videoWidth) return;
    
    const displayArea = getVideoDisplayArea();
    if (!displayArea) return;
    
    const { displayWidth, displayHeight, offsetX, offsetY, containerRect } = displayArea;
    
    // Get cursor position relative to container
    let cursorX = e.clientX - containerRect.left;
    let cursorY = e.clientY - containerRect.top;
    
    // Check if cursor is within video display area (not in letterbox/pillarbox)
    if (cursorX < offsetX || cursorY < offsetY || 
        cursorX > (offsetX + displayWidth) || 
        cursorY > (offsetY + displayHeight)) {
        return; // Ignore clicks outside video area
    }
    
    // Calculate relative position within video display area (0-1)
    const relativeX = (cursorX - offsetX) / displayWidth;
    const relativeY = (cursorY - offsetY) / displayHeight;
    
    // Map to actual video resolution
    const x = Math.floor(relativeX * remoteVideo.videoWidth);
    const y = Math.floor(relativeY * remoteVideo.videoHeight);
    
    // Validate coordinates
    if (!isNaN(x) && !isNaN(y) && x >= 0 && y >= 0 && 
        x < remoteVideo.videoWidth && y < remoteVideo.videoHeight) {
        sendControlInput({ type: 'mouse', data: { x, y, move: true } });
    }
});

remoteVideo.addEventListener('click', e => {
    if (!mouseEnabled || !remoteVideo.videoWidth) return;
    
    const displayArea = getVideoDisplayArea();
    if (!displayArea) return;
    
    const { displayWidth, displayHeight, offsetX, offsetY, containerRect } = displayArea;
    
    // Get cursor position relative to container
    let cursorX = e.clientX - containerRect.left;
    let cursorY = e.clientY - containerRect.top;
    
    // Check if cursor is within video display area
    if (cursorX < offsetX || cursorY < offsetY || 
        cursorX > (offsetX + displayWidth) || 
        cursorY > (offsetY + displayHeight)) {
        return; // Ignore clicks outside video area
    }
    
    // Calculate relative position within video display area (0-1)
    const relativeX = (cursorX - offsetX) / displayWidth;
    const relativeY = (cursorY - offsetY) / displayHeight;
    
    // Map to actual video resolution
    const x = Math.floor(relativeX * remoteVideo.videoWidth);
    const y = Math.floor(relativeY * remoteVideo.videoHeight);
    
    // Validate and send click
    if (!isNaN(x) && !isNaN(y) && x >= 0 && y >= 0 && 
        x < remoteVideo.videoWidth && y < remoteVideo.videoHeight) {
        sendControlInput({
            type: 'mouse',
            data: { x, y, click: true, button: 'left' }
        });
    }
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