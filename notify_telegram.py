import os
import sys
from pathlib import Path
from dotenv import load_dotenv

try:
    import httpx
except ImportError:
    httpx = None

def get_config():
    # Load JVPS env
    jvps_env = Path(__file__).resolve().parent / '.env'
    if jvps_env.exists():
        load_dotenv(jvps_env)
        
    # Load Bane-Bot env for Telegram credentials
    bane_env = Path(__file__).resolve().parents[1] / 'bane-bot' / '.env'
    if bane_env.exists():
        load_dotenv(bane_env)
        
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('STARTUP_NOTIFY_TELEGRAM_CHAT_ID') or os.getenv('ALLOWED_USERS') or os.getenv('FACEBOOK_REPLY_NOTIFY_TELEGRAM_CHAT_ID')
    if chat_id and ',' in chat_id:
        chat_id = chat_id.split(',')[0].strip()
        
    room_name = os.getenv('JVPS_ROOM_NAME', 'SERVER-1:Deployed_Services')
    password = os.getenv('JVPS_PASSWORD', 'JaysonMaster2026!')
    base_url = os.getenv('JVPS_PUBLIC_URL', 'https://jvps.jayson056.space').rstrip('/')
    session_id = 'SESSION-SERVER-1-DEPLOYED-SERVICES'
    
    return {
        'bot_token': bot_token,
        'chat_id': chat_id,
        'room_name': room_name,
        'password': password,
        'base_url': base_url,
        'session_id': session_id
    }

def send_telegram_notification():
    cfg = get_config()
    if not cfg['bot_token'] or not cfg['chat_id']:
        print(f"[WARN] Cannot send Telegram notification: missing bot_token or chat_id")
        return False
        
    viewer_link = f"{cfg['base_url']}/auto_viewer/{cfg['session_id']}?pwd={cfg['password']}"
    
    message = (
        f"🖥️ <b>JVPS Desktop Remote LIVE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>Room:</b> <code>{cfg['room_name']}</code>\n"
        f"🔗 <b>Viewer Link:</b> <a href=\"{viewer_link}\">{viewer_link}</a>\n"
        f"🔑 <b>Password:</b> <code>{cfg['password']}</code>\n"
        f"🔊 <b>Audio:</b> Enabled (Live Desktop/Mic)\n"
        f"🖱️ <b>Control:</b> Isolated Virtual Cursor (Host Protected)\n"
        f"📋 <b>Clipboard:</b> Bidirectional Copy/Paste\n"
        f"🕒 <b>Broadcaster:</b> Active 24/7 (Headless)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    url = f"https://api.telegram.org/bot{cfg['bot_token']}/sendMessage"
    payload = {
        'chat_id': cfg['chat_id'],
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        if httpx:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, json=payload)
                data = resp.json()
                if data.get('ok'):
                    print(f"[INFO] Telegram notification sent successfully to {cfg['chat_id']}")
                    return True
                else:
                    print(f"[ERROR] Telegram API error: {data}")
                    return False
        else:
            import urllib.request
            import json
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = json.loads(response.read().decode())
                return bool(res_data.get('ok'))
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram notification: {e}")
        return False

if __name__ == '__main__':
    send_telegram_notification()
