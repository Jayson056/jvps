// static/js/auto_viewer.js
// Auto-viewer with enhanced status, latency tracking, and clipboard support

let lastPingTime = 0;
let latencyHistory = [];

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
        latencyDisplay.textContent = `Latency: ${avgLatency}ms`;
    }
});

// Send periodic ping
setInterval(() => {
    if (socket.connected) {
        socket.emit('ping_request', { timestamp: Date.now() });
    }
}, 2000);

// Status update function
function updateStatus(text, status) {
    const dot = document.getElementById('statusDot');
    const label = document.getElementById('statusText');
    
    if (dot) {
        dot.className = 'status-dot ' + status;
    }
    if (label) {
        label.textContent = text;
    }
}

// Window controls
document.addEventListener('DOMContentLoaded', () => {
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
