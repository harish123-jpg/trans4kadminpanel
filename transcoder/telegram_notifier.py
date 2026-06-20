# transcoder/telegram_notifier.py
import requests
from django.conf import settings
from datetime import datetime
import time

def get_token():
    return getattr(settings, "TELEGRAM_BOT_TOKEN", None)

def get_chat_id():
    return getattr(settings, "TELEGRAM_CHAT_ID", None)

def send_channel_alert(stream_name, status, max_retries=2):
    """
    Send Telegram alert and return True on success, False on failure.
    This logs response text to stdout for debugging and retries a couple times.
    """

    token = get_token()
    chat_id = get_chat_id()

    if not token or not chat_id:
        print("Telegram token/chat missing:", token, chat_id)
        return False

    if status == 'stopped':
        message = (
            f"🚨 *Stream Alert!*\n"
            f"Channel: *{stream_name}*\n"
            f"Status: ❌ *Stopped*\n"
            f"Server: `{settings.SERVER_NAME}`\n"
            f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
    else:
        message = (
            f"✅ *Stream Running*\n"
            f"Channel: *{stream_name}*\n"
            f"Status: Running\n"
            f"Server: `{settings.SERVER_NAME}`\n"
            f"Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(url, data=payload, timeout=6)
            print(f"[telegram] attempt {attempt} -> status_code: {resp.status_code}")
            print(f"[telegram] response: {resp.text}")
            if resp.ok:
                return True
        except Exception as e:
            print(f"[telegram] send error attempt {attempt}:", e)
        # small backoff
        time.sleep(1)

    return False

