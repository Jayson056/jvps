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

// Control States: DEFAULT OFF to sanitize and protect host cursor!
let mouseEnabled = false;
let kbdEnabled = false;
let isMouseDown = false;

// Virtual cursor element for isolated pointer
let virtualCursor = null;

function initVirtualCursor() {
    if (!virtualCursor && remoteVideo.parentElement) {
        virtualCursor = document.createElement('div');
        virtualCursor.id = 'virtualCursor';
        virtualCursor.style.position = 'absolute';
        virtualCursor.style.width = '12px';
        virtualCursor.style.height = '12px';
        virtualCursor.style.borderRadius = '50%';
        virtualCursor.style.background = '#3498db';
        virtualCursor.style.border = '2px solid #ffffff';
        virtualCursor.style.boxShadow = '0 0 6px rgba(0,0,0,0.6)';
        virtualCursor.style.pointerEvents = 'none';
        virtualCursor.style.zIndex = '9999';
        virtualCursor.style.display = 'none';
        virtualCursor.style.transform = 'translate(-50%, -50%)';
        virtualCursor.style.transition = 'width 0.1s, height 0.1s, background 0.1s';
        
        remoteVideo.parentElement.style.position = 'relative';
        remoteVideo.parentElement.appendChild(virtualCursor);
    }
}

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
        socket.emit('join_session', {
            session_id: sessionId,
            device_id: deviceId,
            auto_approve: window.AUTO_APPROVE || false
        });
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

// Broadcaster reconnecting alert
socket.on('broadcaster_reconnecting', () => {
    console.log("[INFO] Broadcaster is reconnecting...");
    const statusText = document.getElementById('statusText');
    if (statusText) statusText.textContent = 'Broadcaster reconnecting...';
    const statusDot = document.getElementById('statusDot');
    if (statusDot) statusDot.className = 'status-dot connecting';
});

socket.on('broadcaster_ready', () => {
    console.log("[INFO] Broadcaster is ready. Requesting session connection...");
    if (sessionId) {
        socket.emit('join_session', {
            session_id: sessionId,
            device_id: deviceId,
            auto_approve: window.AUTO_APPROVE || false
        });
    }
});

// ---------------------------
// 2. WebRTC Setup
// ---------------------------
function startWebRTC() {
    if (pc) {
        try { pc.close(); } catch(e) {}
    }

    pc = new RTCPeerConnection({
        iceServers: [
            { urls: "stun:stun.l.google.com:19302" },
            { urls: "stun:stun1.l.google.com:19302" }
        ]
    });

    // Handle incoming video & audio stream
    pc.ontrack = event => {
        console.log("[INFO] Remote stream received, track kind:", event.track.kind);
        if (remoteVideo.srcObject !== event.streams[0]) {
            remoteVideo.srcObject = event.streams[0];
            remoteVideo.play().then(() => {
                console.log("[INFO] Video & audio stream playback started");
            }).catch(err => {
                console.warn("[WARN] Autoplay with sound prevented by browser:", err);
                // Attempt muted play if sound was blocked by browser policy
                remoteVideo.muted = true;
                remoteVideo.play();
                showUnmuteBtn();
            });
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
        if (pc.connectionState === 'connected') {
            const statusDot = document.getElementById('statusDot');
            if (statusDot) statusDot.className = 'status-dot connected';
            const statusText = document.getElementById('statusText');
            if (statusText) statusText.textContent = 'Connected (Live 24/7)';
        } else if (pc.connectionState === 'disconnected') {
            const statusDot = document.getElementById('statusDot');
            if (statusDot) statusDot.className = 'status-dot connecting';
        }
    };
}

function showUnmuteBtn() {
    const soundBtn = document.getElementById('btnSound');
    if (soundBtn) {
        soundBtn.innerHTML = '🔇 Unmute Audio';
        soundBtn.classList.remove('btn-secondary');
        soundBtn.classList.add('btn-warning');
    }
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
            }
        } catch (err) {
            console.error("[ERROR] Candidate error:", err);
        }
    }
});

// ---------------------------
// 4. Remote Control Logic (SANITIZED & ISOLATED)
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
        displayWidth = rect.width;
        displayHeight = rect.width / videoAspect;
        offsetY = (rect.height - displayHeight) / 2;
    } else {
        displayHeight = rect.height;
        displayWidth = rect.height * videoAspect;
        offsetX = (rect.width - displayWidth) / 2;
    }
    
    return { displayWidth, displayHeight, offsetX, offsetY, containerRect: rect };
}

// Translate client mouse position to video coordinates
function getScaledCoordinates(e) {
    const displayArea = getVideoDisplayArea();
    if (!displayArea) return null;
    
    const { displayWidth, displayHeight, offsetX, offsetY, containerRect } = displayArea;
    const cursorX = e.clientX - containerRect.left;
    const cursorY = e.clientY - containerRect.top;
    
    if (cursorX < offsetX || cursorY < offsetY || 
        cursorX > (offsetX + displayWidth) || 
        cursorY > (offsetY + displayHeight)) {
        return null; // Outside actual video frame
    }
    
    const relativeX = (cursorX - offsetX) / displayWidth;
    const relativeY = (cursorY - offsetY) / displayHeight;
    const x = Math.floor(relativeX * remoteVideo.videoWidth);
    const y = Math.floor(relativeY * remoteVideo.videoHeight);
    
    return { x, y, cursorX, cursorY };
}

// Virtual Cursor Mousemove:
// IMPORTANT SANITIZATION: Passive hover moves NEVER send moveTo to the host!
remoteVideo.addEventListener('mousemove', e => {
    initVirtualCursor();
    const coords = getScaledCoordinates(e);
    if (!coords) {
        if (virtualCursor) virtualCursor.style.display = 'none';
        return;
    }
    
    // Update client virtual pointer
    if (virtualCursor) {
        virtualCursor.style.display = 'block';
        virtualCursor.style.left = coords.cursorX + 'px';
        virtualCursor.style.top = coords.cursorY + 'px';
        virtualCursor.style.background = mouseEnabled ? '#e74c3c' : '#3498db';
    }
    
    // Only send drag movement if mouse button is held down AND control is ON!
    if (mouseEnabled && isMouseDown) {
        sendControlInput({
            type: 'mouse',
            data: { x: coords.x, y: coords.y, drag: true }
        });
    }
});

remoteVideo.addEventListener('mouseleave', () => {
    if (virtualCursor) virtualCursor.style.display = 'none';
    isMouseDown = false;
});

// Click listener
remoteVideo.addEventListener('click', e => {
    if (!mouseEnabled) return;
    const coords = getScaledCoordinates(e);
    if (!coords) return;
    
    sendControlInput({
        type: 'mouse',
        data: { x: coords.x, y: coords.y, click: true, button: 'left' }
    });
});

// Double-click listener
remoteVideo.addEventListener('dblclick', e => {
    if (!mouseEnabled) return;
    const coords = getScaledCoordinates(e);
    if (!coords) return;
    
    sendControlInput({
        type: 'mouse',
        data: { x: coords.x, y: coords.y, dblclick: true, button: 'left' }
    });
});

// Right click listener
remoteVideo.addEventListener('contextmenu', e => {
    if (!mouseEnabled) return;
    e.preventDefault(); // Don't show browser right-click menu
    const coords = getScaledCoordinates(e);
    if (!coords) return;
    
    sendControlInput({
        type: 'mouse',
        data: { x: coords.x, y: coords.y, click: true, button: 'right' }
    });
});

// Mouse down / up for dragging
remoteVideo.addEventListener('mousedown', e => {
    isMouseDown = true;
    if (!mouseEnabled) return;
    const coords = getScaledCoordinates(e);
    if (!coords) return;
    
    const btn = e.button === 2 ? 'right' : 'left';
    sendControlInput({
        type: 'mouse',
        data: { x: coords.x, y: coords.y, mousedown: true, button: btn }
    });
});

remoteVideo.addEventListener('mouseup', e => {
    isMouseDown = false;
    if (!mouseEnabled) return;
    const coords = getScaledCoordinates(e);
    if (!coords) return;
    
    const btn = e.button === 2 ? 'right' : 'left';
    sendControlInput({
        type: 'mouse',
        data: { x: coords.x, y: coords.y, mouseup: true, button: btn }
    });
});

// Wheel / Scroll listener
remoteVideo.addEventListener('wheel', e => {
    if (!mouseEnabled) return;
    e.preventDefault();
    const coords = getScaledCoordinates(e);
    if (!coords) return;
    
    sendControlInput({
        type: 'mouse',
        data: { x: coords.x, y: coords.y, wheel: true, deltaY: e.deltaY }
    });
}, { passive: false });

// Keyboard listeners
window.addEventListener('keydown', e => {
    if (!kbdEnabled) return;
    // Don't capture inputs if user is typing in a text input box
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    // Prevent browser defaults for common navigation keys
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Tab', 'Space'].includes(e.code)) {
        e.preventDefault();
    }
    sendControlInput({ type: 'keyboard', data: { key: e.key, action: 'down' } });
});

window.addEventListener('keyup', e => {
    if (!kbdEnabled) return;
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    sendControlInput({ type: 'keyboard', data: { key: e.key, action: 'up' } });
});

// ---------------------------
// 5. Remote Clipboard Support
// ---------------------------
function sendClipboardToHost(text) {
    if (!text) return;
    socket.emit('clipboard_set', { text: text });
}

function requestClipboardFromHost() {
    socket.emit('clipboard_get');
}

socket.on('clipboard_ack', data => {
    if (data.success) {
        showToast("✓ Sent text to Host Clipboard!");
    }
});

socket.on('clipboard_data', data => {
    if (data.text) {
        navigator.clipboard.writeText(data.text).then(() => {
            showToast("✓ Copied Host Clipboard to your device!");
        }).catch(() => {
            prompt("Host Clipboard content (Ctrl+C to copy):", data.text);
        });
    } else {
        showToast("Host clipboard is empty");
    }
});

// Listen for Ctrl+V paste while focused on viewer
window.addEventListener('paste', e => {
    const text = (e.clipboardData || window.clipboardData).getData('text');
    if (text) {
        sendClipboardToHost(text);
        showToast("✓ Pasted to Host Clipboard!");
    }
});

// Toast notification helper
function showToast(msg) {
    let toast = document.getElementById('viewerToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'viewerToast';
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.background = '#2c3e50';
        toast.style.color = '#fff';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '8px';
        toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.4)';
        toast.style.zIndex = '99999';
        toast.style.fontSize = '14px';
        toast.style.fontWeight = 'bold';
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

// ---------------------------
// 6. UI Controls & Initialization
// ---------------------------
document.addEventListener('DOMContentLoaded', () => {
    initVirtualCursor();

    // Toggle Sound Button
    const btnSound = document.getElementById('btnSound');
    if (btnSound) {
        btnSound.addEventListener('click', () => {
            remoteVideo.muted = !remoteVideo.muted;
            btnSound.innerHTML = remoteVideo.muted ? '🔇 Sound: MUTED' : '🔊 Sound: ON';
            btnSound.classList.toggle('btn-primary', !remoteVideo.muted);
            btnSound.classList.toggle('btn-secondary', remoteVideo.muted);
        });
    }

    // Toggle Mouse Control
    const toggleMouseBtn = document.getElementById('toggleMouse');
    if (toggleMouseBtn) {
        // Reflect default OFF
        toggleMouseBtn.innerHTML = '🖱️ Mouse: VIEW ONLY';
        toggleMouseBtn.classList.remove('btn-primary');
        toggleMouseBtn.classList.add('btn-secondary');

        toggleMouseBtn.addEventListener('click', () => {
            mouseEnabled = !mouseEnabled;
            if (mouseEnabled) {
                toggleMouseBtn.innerHTML = '🖱️ Mouse: CONTROL';
                toggleMouseBtn.classList.remove('btn-secondary');
                toggleMouseBtn.classList.add('btn-danger');
                showToast("⚠️ Control Mode: Mouse clicks will interact with remote host");
            } else {
                toggleMouseBtn.innerHTML = '🖱️ Mouse: VIEW ONLY';
                toggleMouseBtn.classList.remove('btn-danger');
                toggleMouseBtn.classList.add('btn-secondary');
                showToast("View-Only: Host cursor protected");
            }
        });
    }

    // Toggle Keyboard Control
    const toggleKbdBtn = document.getElementById('toggleKbd');
    if (toggleKbdBtn) {
        toggleKbdBtn.innerHTML = '⌨️ Kbd: OFF';
        toggleKbdBtn.classList.remove('btn-primary');
        toggleKbdBtn.classList.add('btn-secondary');

        toggleKbdBtn.addEventListener('click', () => {
            kbdEnabled = !kbdEnabled;
            toggleKbdBtn.innerHTML = kbdEnabled ? '⌨️ Kbd: ON' : '⌨️ Kbd: OFF';
            toggleKbdBtn.classList.toggle('btn-danger', kbdEnabled);
            toggleKbdBtn.classList.toggle('btn-secondary', !kbdEnabled);
        });
    }

    // Clipboard Paste Button
    const btnPaste = document.getElementById('btnPaste');
    if (btnPaste) {
        btnPaste.addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                if (text) {
                    sendClipboardToHost(text);
                } else {
                    const manualText = prompt("Enter text to send to Host Clipboard:");
                    if (manualText) sendClipboardToHost(manualText);
                }
            } catch(e) {
                const manualText = prompt("Enter text to send to Host Clipboard:");
                if (manualText) sendClipboardToHost(manualText);
            }
        });
    }

    // Clipboard Copy from Host Button
    const btnCopy = document.getElementById('btnCopy');
    if (btnCopy) {
        btnCopy.addEventListener('click', () => {
            requestClipboardFromHost();
        });
    }
});