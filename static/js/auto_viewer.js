// static/js/auto_viewer.js
// Auto-viewer with enhanced status and latency tracking

let lastPingTime = 0;
let latencyHistory = [];

// Override status tracking
const originalConnect = socket.on;

socket.on('connect', () => {
    console.log("[INFO] Connected to server");
    updateStatus('Connecting to device...', 'connecting');
    socket.emit('register_device', { role: 'viewer', device_id: null });
});

socket.on('device_registered', (data) => {
    deviceId = data.device_id;
    console.log("[INFO] Viewer registered with ID:", deviceId);
    updateStatus('Joining session...', 'connecting');

    if (sessionId) {
        console.log("[INFO] Joining session:", sessionId);
        socket.emit('join_session', { 
            session_id: sessionId, 
            device_id: deviceId,
            auto_approve: window.AUTO_APPROVE || false
        });
    }
});

socket.on('viewer_approved', (data) => {
    if (data.approved) {
        console.log("[INFO] Approved! Starting WebRTC...");
        updateStatus('Connected to device', 'connected');
        startWebRTC();
    } else {
        alert("Access denied by remote device.");
        updateStatus('Access Denied', 'disconnected');
    }
});

socket.on('disconnect', () => {
    console.log("[WARNING] Disconnected from server");
    updateStatus('Connection Lost', 'disconnected');
});

// Status update function
function updateStatus(text, status) {
    const dot = document.getElementById('statusDot');
    const label = document.getElementById('statusText');
    
    if (dot) {
        dot.className = 'status-dot ' + status;
    }
    if (label) {
        label.innerHTML = text;
    }
}

// Latency tracking
socket.on('ping', () => {
    socket.emit('pong', { timestamp: Date.now() });
});

socket.on('pong_response', (data) => {
    const latency = Date.now() - data.timestamp;
    latencyHistory.push(latency);
    if (latencyHistory.length > 10) latencyHistory.shift();
    
    const avgLatency = Math.round(latencyHistory.reduce((a, b) => a + b, 0) / latencyHistory.length);
    const latencyDisplay = document.getElementById('latency');
    if (latencyDisplay) {
        latencyDisplay.innerHTML = `<i class="fas fa-tachometer-alt"></i> Latency: ${avgLatency}ms`;
    }
});

// Send periodic ping
setInterval(() => {
    if (socket.connected) {
        socket.emit('ping_request', { timestamp: Date.now() });
    }
}, 2000);

// Enhanced button handling
document.addEventListener('DOMContentLoaded', () => {
    // Toggle Mouse
    const toggleMouseBtn = document.getElementById('toggleMouse');
    if (toggleMouseBtn) {
        toggleMouseBtn.addEventListener('click', () => {
            mouseEnabled = !mouseEnabled;
            toggleMouseBtn.innerHTML = `<i class="fas fa-mouse"></i> Mouse: ${mouseEnabled ? 'ON' : 'OFF'}`;
            toggleMouseBtn.classList.toggle('btn-primary');
            toggleMouseBtn.classList.toggle('btn-warning');
        });
    }

    // Toggle Keyboard
    const toggleKbdBtn = document.getElementById('toggleKbd');
    if (toggleKbdBtn) {
        toggleKbdBtn.addEventListener('click', () => {
            kbdEnabled = !kbdEnabled;
            toggleKbdBtn.innerHTML = `<i class="fas fa-keyboard"></i> Keyboard: ${kbdEnabled ? 'ON' : 'OFF'}`;
            toggleKbdBtn.classList.toggle('btn-primary');
            toggleKbdBtn.classList.toggle('btn-warning');
        });
    }

    // Fullscreen
    const btnFull = document.getElementById('btnFull');
    if (btnFull) {
        btnFull.addEventListener('click', () => {
            if (remoteVideo.requestFullscreen) {
                remoteVideo.requestFullscreen();
            } else if (remoteVideo.webkitRequestFullscreen) {
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
});
