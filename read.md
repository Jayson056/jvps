# OmniStream Pro — Remote Desktop & Control

OmniStream Pro is a low-latency screen-sharing application that uses **WebRTC** for video streaming and a **Python-based Agent** for physical remote control (Mouse/Keyboard) via PyAutoGUI.

## 1. Project Structure

```text
BROADCAST/
├── app.py                 # Flask-SocketIO Signaling Server
├── agent/
│   └── screenshare.py     # Python Agent (Handles physical mouse/keys)
├── static/
│   ├── js/
│   │   ├── webrtc_broadcaster.js
│   │   └── webrtc_viewer.js
│   └── css/
│       └── common.css
└── templates/
    ├── home.html
    ├── view_list.html
    └── view_screen.html

```

## 2. Prerequisites

* **Python 3.x**
* **Virtual Environment** (Recommended)
* **Dependencies**:
```bash
pip install flask flask-socketio eventlet pyautogui python-socketio requests

```



## 3. How to Run

### Step 1: Start the Signaling Server

The server coordinates the connection between the broadcaster, the viewer, and the python agent.

```bash
python app.py

```

*The server will start on `http://localhost:58247`.*

### Step 2: Start the Broadcaster (Web)

1. Open your browser to `http://localhost:58247/broadcast/new`.
2. Grant permissions for screen sharing.
3. **Note your Broadcaster ID** from the browser console (F12).
*Example: `0bf5f08e-67ea-4b43-9b92-813065b75234*`

### Step 3: Start the Python Agent

The agent is required to move the physical mouse on the broadcaster's computer.

1. Open `agent/screenshare.py`.
2. Update the `device_id` variable with the ID from Step 2.
3. Run the agent:
```bash
python agent/screenshare.py

```



### Step 4: Access as a Viewer

1. From another device (or tab), go to `http://<your-ip>:58247/view_list`.
2. Click on the active session.
3. You can now see the screen. Moving your mouse over the video will move the physical mouse on the broadcaster's machine.

## 4. How it Works

1. **Video (WebRTC)**: The Browser uses `getDisplayMedia` to capture the screen and streams it directly to the viewer via a Peer-to-Peer connection.
2. **Signaling (Socket.IO)**: The server facilitates the "handshake" between peers.
3. **Control (PyAutoGUI)**:
* The **Viewer** captures mouse coordinates and sends them to the **Server**.
* The **Server** relays these coordinates to the **Python Agent**.
* The **Agent** uses `pyautogui.moveTo()` to execute the movement on the OS level.



## 5. Troubleshooting

* **Mouse not moving?** Ensure the `device_id` in `screenshare.py` matches the ID in the Broadcaster's browser console.
* **Connection Failed?** Ensure you have installed the `requests` package: `pip install requests`.
* **Latency?** Ensure the Broadcaster and Viewer are on a stable network; WebRTC works best with a direct connection.

## 6. Safety Warning

This application allows remote control of your computer. Do not share your Broadcast URL or Session ID with anyone you do not trust. Use `Ctrl+C` in the terminal to kill the Python Agent at any time to regain exclusive control of your mouse.