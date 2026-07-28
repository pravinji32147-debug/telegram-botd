import requests
import json
import time

# ==========================
# Configuration
# ==========================

BOT_TOKEN = "8722131069:AAEXcnLVSIRC3SkP3bmT_QV_fvVTDbL336U"
EXTERNAL_API_URL = "curl -X GET \
  "https://www.apicentre.in/api/aadhaar_to_pan?api_key=b067fcc9d14f21ef087f470d8df5ebb38e76e4227a635979b678b8edf4f5&aadhaar_no=335400206902" \
  -H "Accept: application/json""

BASE_URL = "https://api.telegram.org/bot" + BOT_TOKEN

# ==========================
# Keyboard
# ==========================

REPLY_KEYBOARD = {
    "keyboard": [
        [
            {"text": "📱 Phone Lookup"}
        ]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}


# ==========================
# Telegram Functions
# ==========================

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = BASE_URL + "/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup is not None:
        payload["reply_markup"] = json.dumps(reply_markup)

    if parse_mode is not None:
        payload["parse_mode"] = parse_mode

    try:
        requests.post(url, data=payload, timeout=30)
    except Exception as e:
        print("Send Message Error:", e)


def get_updates(offset=None):
    url = BASE_URL + "/getUpdates"

    params = {
        "timeout": 30
    }

    if offset is not None:
        params["offset"] = offset

    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        print("Polling Error:", e)
        return {"ok": False, "result": []}


# ==========================
# External HTTPS API Helper
# ==========================

def phone_lookup(number):
    """
    Dummy HTTPS API request.
    Replace EXTERNAL_API_URL with your HTTPS endpoint.

    Example:
    https://example.com/api?mobile=9876543210
    """

    try:
        response = requests.get(
            EXTERNAL_API_URL,
            params={"mobile": number},
            timeout=30,
            verify=True
        )

        return response.json()

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==========================
# Validation
# ==========================

def is_valid_mobile(number):
    return number.isdigit() and len(number) == 10


# ==========================
# Main Bot
# ==========================

def main():
    print("Bot Started...")

    offset = None

    while True:
        updates = get_updates(offset)

        if updates.get("ok"):

            for update in updates.get("result", []):

                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]

                chat_id = message["chat"]["id"]

                text = message.get("text", "").strip()

                # ----------------------
                # /start
                # ----------------------
                if text == "/start":

                    welcome = (
                        "👋 Welcome!\n\n"
                        "Use the button below to perform a phone lookup."
                    )

                    send_message(
                        chat_id,
                        welcome,
                        reply_markup=REPLY_KEYBOARD
                    )

                # ----------------------
                # Button
                # ----------------------
                elif text == "📱 Phone Lookup":

                    send_message(
                        chat_id,
                        "📞 Send 10 digit mobile number:"
                    )

                # ----------------------
                # Phone Number
                # ----------------------
                elif is_valid_mobile(text):

                    send_message(
                        chat_id,
                        "🔍 Looking up..."
                    )

                    result = phone_lookup(text)

                    formatted = json.dumps(
                        result,
                        indent=4,
                        ensure_ascii=False
                    )

                    send_message(
                        chat_id,
                        "<pre>" + formatted + "</pre>",
                        parse_mode="HTML"
                    )

                # ----------------------
                # Invalid Input
                # ----------------------
                else:

                    send_message(
                        chat_id,
                        "❌ Invalid input.\n\nPlease send a valid 10 digit mobile number or use /start."
                    )

        time.sleep(1)


# ==========================
# Run
# ==========================

if __name__ == "__main__":
    main()
