// static/js/webrtc_broadcaster.js

const socket = io();  // Connect to Flask Socket.IO
let localStream = null;
let peers = {};  // viewer_id -> RTCPeerConnection
let deviceId = null;

// ---------------------------
// 1. Capture Screen on Load
// ---------------------------
async function getLocalStream() {
    try {
        console.log("[INFO] Requesting screen capture...");
        // Capture screen + system audio
        localStream = await navigator.mediaDevices.getDisplayMedia({
            video: { cursor: "always" },
            audio: true
        });

        const videoElem = document.getElementById('localVideo');
        if (videoElem) {
            videoElem.srcObject = localStream;
            videoElem.play();
        }
        console.log("[INFO] Local stream captured successfully");

        // Safety: If stream stops (user clicks 'Stop Sharing' in browser bar)
        localStream.getVideoTracks()[0].onended = () => {
            stopBroadcast();
        };

    } catch (err) {
        console.error("[ERROR] Failed to get local stream:", err);
        alert("Screen capture is required for broadcasting.");
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

    // Add local screen tracks to the connection
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
        if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
            delete peers[viewerId];
        }
    };

    return pc;
}

// ---------------------------
// 3. Socket.IO Event Handlers
// ---------------------------
socket.on('connect', () => {
    console.log("[INFO] Connected to signaling server");
    socket.emit('register_device', { 
        role: 'broadcaster', 
        device_id: window.deviceId 
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
    getLocalStream();
    const stopBtn = document.getElementById('stopBtn');
    if (stopBtn) stopBtn.addEventListener('click', stopBroadcast);
});