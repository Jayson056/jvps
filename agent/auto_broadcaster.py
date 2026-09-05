# apps/jvps/agent/auto_broadcaster.py
"""
JVPS 24/7 Headless Auto-Broadcaster
Streams the entire machine desktop screen and audio continuously without opening a visible browser window.
"""

import asyncio
import os
import sys
import time
import socket
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Load environment configuration
jvps_dir = Path(__file__).resolve().parents[1]
load_dotenv(jvps_dir / '.env')

PORT = int(os.getenv("PORT", 50011))
ROOM_NAME = os.getenv("JVPS_ROOM_NAME", "SERVER-1:Deployed_Services")
PASSWORD = os.getenv("JVPS_PASSWORD", "JaysonMaster2026!")
DEVICE_ID = "DEV-SERVER-1"
BROADCAST_URL = f"http://127.0.0.1:{PORT}/broadcast/{DEVICE_ID}"

def is_port_open(port: int, host: str = "127.0.0.1", timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def wait_for_server(port: int, timeout_sec: int = 60) -> bool:
    print(f"[INFO] Waiting for JVPS server on port {port}...")
    start = time.time()
    while time.time() - start < timeout_sec:
        if is_port_open(port):
            print(f"[INFO] JVPS server is online at port {port}")
            return True
        time.sleep(1)
    return False

def trigger_telegram_notification():
    try:
        notify_script = jvps_dir / "notify_telegram.py"
        if notify_script.exists():
            import subprocess
            subprocess.Popen(
                [sys.executable, str(notify_script)],
                cwd=str(jvps_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("[INFO] Triggered Telegram notification via Bane-V3")
    except Exception as e:
        print(f"[WARN] Could not trigger Telegram notification: {e}")

async def run_broadcaster(single_test: bool = False):
    from playwright.async_api import async_playwright

    print(f"[INFO] Initializing JVPS 24/7 Headless Live Broadcaster")
    print(f"[INFO] Room: {ROOM_NAME}")
    print(f"[INFO] Broadcaster URL: {BROADCAST_URL}")

    # 1. Wait for server to bind port
    if not wait_for_server(PORT):
        print(f"[ERROR] JVPS server did not start on port {PORT}. Aborting.")
        return

    notification_sent = False

    while True:
        try:
            async with async_playwright() as p:
                print("[INFO] Launching invisible background Chrome instance...")
                browser = await p.chromium.launch(
                    channel="chrome",
                    headless=False,  # Invisible off-screen window (headless blocks WebRTC capture on Windows)
                    args=[
                        "--auto-select-desktop-capture-source=Entire screen",
                        "--enable-usermedia-screen-capturing",
                        "--allow-http-screen-capture",
                        "--use-fake-ui-for-media-stream",
                        "--autoplay-policy=no-user-gesture-required",
                        "--disable-background-timer-throttling",
                        "--disable-backgrounding-occluded-windows",
                        "--disable-renderer-backgrounding",
                        "--disable-features=CalculateNativeWinOcclusion",
                        "--window-position=-32000,-32000",
                        "--window-size=1280,720",
                    ]
                )

                context = await browser.new_context(
                    permissions=["camera", "microphone"],
                    ignore_https_errors=True
                )
                page = await context.new_page()

                # Catch console messages for diagnostics
                page.on("console", lambda msg: print(f"[BROWSER_LOG] {msg.type}: {msg.text}"))
                page.on("pageerror", lambda err: print(f"[BROWSER_ERROR] {err}"))

                print(f"[INFO] Navigating to {BROADCAST_URL}...")
                await page.goto(BROADCAST_URL, wait_until="networkidle")

                # Wait for stream capture confirmation
                capture_ready = False
                for _ in range(20):
                    status = await page.evaluate("""() => {
                        const el = document.getElementById('broadcastStatus');
                        const v = document.getElementById('localVideo');
                        const hasStream = v && v.srcObject && v.srcObject.active;
                        return { text: el ? el.textContent : '', active: !!hasStream };
                    }""")
                    if status.get('active'):
                        print(f"[INFO] Live screen & audio stream ACTIVE! Status: {status.get('text')}")
                        capture_ready = True
                        break
                    await asyncio.sleep(1)

                if capture_ready and not notification_sent:
                    trigger_telegram_notification()
                    notification_sent = True

                if single_test:
                    print("[INFO] Test run successful. Closing browser.")
                    await browser.close()
                    return

                # 24/7 Watchdog Loop
                print("[INFO] Broadcaster running 24/7. Monitoring stream health...")
                while True:
                    await asyncio.sleep(15)
                    # Check if page is alive and stream is active
                    is_active = await page.evaluate("""() => {
                        const v = document.getElementById('localVideo');
                        return v && v.srcObject && v.srcObject.active;
                    }""")
                    if not is_active:
                        print("[WARN] Local stream lost activity! Triggering reconnect...")
                        break

                await browser.close()

        except Exception as e:
            print(f"[ERROR] Broadcaster exception: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    single_run = "--test-once" in sys.argv
    try:
        asyncio.run(run_broadcaster(single_test=single_run))
    except KeyboardInterrupt:
        print("[INFO] Auto-broadcaster stopped by user.")
        sys.exit(0)
