// static/js/webrtc_broadcaster.js

const socket = io();  // Connect to Flask Socket.IO
let localStream = null;
let peers = {};  // viewer_id -> RTCPeerConnection
let deviceId = null;
let currentSource = null;   // 'screen' | 'environment' (back cam) | 'user' (front cam)

// ---------------------------
// 0. Capability / device detection
// ---------------------------
function isMobileDevice() {
    return /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
}

function supportsScreenShare() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia);
}

function supportsCamera() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
}

function setStatus(message, kind) {
    // kind: 'info' | 'error' | 'success'
    const el = document.getElementById('broadcastStatus');
    if (!el) return;
    el.textContent = message;
    el.dataset.kind = kind || 'info';
}

function showInsecureWarning() {
    const warn = document.getElementById('insecureWarning');
    if (warn) warn.style.display = 'block';
}

// Highlight the button matching the active source
function markActiveSource(source) {
    ['srcScreen', 'srcBack', 'srcFront'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) btn.classList.remove('src-active');
    });
    const map = { screen: 'srcScreen', environment: 'srcBack', user: 'srcFront' };
    const activeBtn = document.getElementById(map[source]);
    if (activeBtn) activeBtn.classList.add('src-active');
}

// ---------------------------
// 1. Capture a stream (screen OR phone camera)
// ---------------------------
async function startCapture(source) {
    // Secure-context guard: getUserMedia / getDisplayMedia are undefined on
    // insecure origins (e.g. http://<lan-ip>:5000 opened from a phone).
    if (!navigator.mediaDevices || (!supportsCamera() && !supportsScreenShare())) {
        showInsecureWarning();
        setStatus('Camera/screen capture is blocked on this connection (needs HTTPS).', 'error');
        console.error('[ERROR] mediaDevices unavailable — not a secure context?');
        return;
    }

    // Fall back to camera if screen share isn't supported (phones).
    if (source === 'screen' && !supportsScreenShare()) {
        console.warn('[WARN] Screen share not supported here — using back camera instead.');
        source = 'environment';
    }
    if (source !== 'screen' && !supportsCamera()) {
        setStatus('This device has no accessible camera.', 'error');
        return;
    }

    try {
        let newStream;
        if (source === 'screen') {
            console.log('[INFO] Requesting screen capture...');
            setStatus('Requesting screen capture permission...', 'info');
            newStream = await navigator.mediaDevices.getDisplayMedia({
                video: { cursor: 'always' },
                audio: false
            });

            // Capture system / microphone audio and attach to the stream
            try {
                const audioStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        echoCancellation: false,
                        autoGainControl: false,
                        noiseSuppression: false
                    }
                });
                audioStream.getAudioTracks().forEach(track => {
                    newStream.addTrack(track);
                    console.log('[INFO] Attached audio track to broadcast:', track.label);
                });
            } catch (aErr) {
                console.warn('[WARN] Audio capture skipped or unavailable:', aErr);
            }
        } else {
            console.log(`[INFO] Requesting camera (${source})...`);
            setStatus('Requesting camera permission...', 'info');
            newStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: { ideal: source } },
                audio: true
            });
        }

        // Swap out any previous stream (source switch).
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
        }
        localStream = newStream;
        currentSource = source;

        const videoElem = document.getElementById('localVideo');
        if (videoElem) {
            videoElem.srcObject = localStream;
            videoElem.play().catch(() => {});
        }

        // Push the new tracks to viewers that are already connected.
        replaceStreamTracks();

        // If the user stops sharing from the browser UI, end the broadcast.
        const videoTrack = localStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.onended = () => stopBroadcast();
        }

        markActiveSource(source);
        const label = source === 'screen' ? 'Screen' :
                      source === 'environment' ? 'Back camera' : 'Front camera';
        setStatus(`✓ Streaming from: ${label}`, 'success');
        console.log('[INFO] Local stream captured successfully:', source);

    } catch (err) {
        console.error('[ERROR] Failed to get local stream:', err);
        if (err && (err.name === 'NotAllowedError' || err.name === 'SecurityError')) {
            setStatus('Permission denied. Allow camera/screen access and try again.', 'error');
        } else if (err && err.name === 'NotFoundError') {
            setStatus('No camera found on this device.', 'error');
        } else if (!window.isSecureContext) {
            showInsecureWarning();
            setStatus('Capture blocked — open this page over HTTPS (see note below).', 'error');
        } else {
            setStatus('Could not start capture: ' + (err.message || err.name), 'error');
        }
    }
}

// Toggle between front and back camera (mobile-friendly).
function switchCamera() {
    if (currentSource === 'screen') {
        startCapture('environment');
        return;
    }
    startCapture(currentSource === 'environment' ? 'user' : 'environment');
}

// Replace outgoing tracks on all existing peer connections without renegotiating.
function replaceStreamTracks() {
    if (!localStream) return;
    for (const id in peers) {
        const pc = peers[id];
        const senders = pc.getSenders();
        localStream.getTracks().forEach(track => {
            const sender = senders.find(s => s.track && s.track.kind === track.kind);
            if (sender) {
                sender.replaceTrack(track).catch(err =>
                    console.error('[ERROR] replaceTrack failed:', err));
            } else {
                pc.addTrack(track, localStream);
            }
        });
    }
}

// ---------------------------
// 2. Create WebRTC Peer Connection
// ---------------------------
function createPeer(viewerId) {
    const pc = new RTCPeerConnection({
        iceServers: [
            { urls: "stun:stun.l.google.com:19302" },
            { urls: "stun:stun1.l.google.com:19302" }
        ]
    });

    // Add local tracks (screen or camera) to the connection
    if (localStream) {
        localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
    }

    // ICE candidate handling
    pc.onicecandidate = event => {
        if (event.candidate) {
            socket.emit('signal', {
                from: deviceId,
                to: viewerId,
                signal: { candidate: event.candidate }
            });
        }
    };

    pc.onconnectionstatechange = () => {
        console.log(`[INFO] Connection state with ${viewerId}: ${pc.connectionState}`);
        if (pc.connectionState === 'failed' || pc.connectionState === 'closed') {
            delete peers[viewerId];
        } else if (pc.connectionState === 'disconnected') {
            // Grace period for transient disconnects (e.g. WiFi hiccup)
            setTimeout(() => {
                if (peers[viewerId] && (peers[viewerId].connectionState === 'disconnected' || peers[viewerId].connectionState === 'failed')) {
                    delete peers[viewerId];
                }
            }, 8000);
        }
    };

    return pc;
}

// ---------------------------
// 3. Socket.IO Event Handlers
// ---------------------------
socket.on('connect', () => {
    console.log("[INFO] Connected to signaling server");

    // Get broadcast data from sessionStorage
    const broadcastData = sessionStorage.getItem('broadcastData');
    let broadcastInfo = {};

    if (broadcastData) {
        broadcastInfo = JSON.parse(broadcastData);
        sessionStorage.removeItem('broadcastData'); // Clean up
    }

    const devId = window.deviceId || broadcastInfo.deviceId;
    socket.emit('register_device', {
        role: 'broadcaster',
        device_id: devId,
        session_id: window.sessionId || broadcastInfo.sessionId,
        password: window.password || broadcastInfo.password,
        room_name: window.roomName || broadcastInfo.roomName,
        broadcaster_name: broadcastInfo.broadcasterName || 'Server Host'
    });
});

socket.on('device_registered', (data) => {
    deviceId = data.device_id;
    console.log("[INFO] Broadcaster registered with ID:", deviceId);
});

// When a viewer joins the session
socket.on('viewer_request', async (data) => {
    const viewerId = data.viewer_id;
    console.log(`[INFO] Incoming connection request from viewer: ${viewerId}`);

    // Auto-approve the viewer
    socket.emit('approve_viewer', {
        viewer_id: viewerId,
        approved: true
    });

    const pc = createPeer(viewerId);
    peers[viewerId] = pc;

    try {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        console.log(`[INFO] Sending WebRTC offer to viewer: ${viewerId}`);
        socket.emit('signal', {
            from: deviceId,
            to: viewerId,
            signal: { sdp: pc.localDescription }
        });
    } catch (err) {
        console.error("[ERROR] Failed to create WebRTC offer:", err);
    }
});

socket.on('signal', async (data) => {
    const fromId = data.from;
    const pc = peers[fromId];

    if (!pc) return;

    if (data.signal.sdp) {
        const desc = new RTCSessionDescription(data.signal.sdp);
        if (desc.type === "answer") {
            await pc.setRemoteDescription(desc);
            console.log("[INFO] WebRTC Handshake complete with viewer:", fromId);
        }
    } else if (data.signal.candidate) {
        try {
            await pc.addIceCandidate(new RTCIceCandidate(data.signal.candidate));
        } catch (err) {
            console.error("[ERROR] Failed to add ICE candidate:", err);
        }
    }
});

// ---------------------------
// 4. REMOTE CONTROL LISTENER
// ---------------------------
// This receives input from the viewer and logs it.
// Your Python Agent (app.py/screenshare.py) will actually execute these.
socket.on('control_input', (action) => {
    console.log("[REMOTE CONTROL] Action received:", action.type, action.data);

    // Logic: If you are running the broadcaster in a browser,
    // the browser cannot move the OS mouse.
    // This event is primarily for the Python Agent to catch.
});

// ---------------------------
// 5. Cleanup and UI
// ---------------------------
function stopBroadcast() {
    for (const id in peers) {
        peers[id].close();
    }
    peers = {};
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }
    console.log("[INFO] Broadcast stopped.");
    window.location.href = "/";
}

// Initialize
window.addEventListener('load', () => {
    // Phones can't reliably screen-share, so default them to the back camera.
    // Desktops keep the original screen-capture behavior.
    if (isMobileDevice() || !supportsScreenShare()) {
        if (!window.isSecureContext && !supportsCamera()) {
            showInsecureWarning();
            setStatus('Open this page over HTTPS to stream from your phone.', 'error');
        } else {
            startCapture('environment');
        }
    } else {
        startCapture('screen');
    }

    const stopBtn = document.getElementById('stopBtn');
    if (stopBtn) stopBtn.addEventListener('click', stopBroadcast);
});
