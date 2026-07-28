import requests
import json
import time

BOT_TOKEN = "8722131069:AAEXcnLVSIRC3SkP3bmT_QV_fvVTDbL336U"
EXTERNAL_API_URL = (
    "https://www.apicentre.in/api/aadhaar_to_pan?"
    "api_key=b067fcc9d14f21ef087f470d8df5ebb38e76e4227a635979b678b8edf4f5"
)

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = f"{BASE_URL}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if reply_markup is not None:
        payload["reply_markup"] = json.dumps(reply_markup)

    if parse_mode is not None:
        payload["parse_mode"] = parse_mode

    try:
        requests.post(url, data=payload, timeout=30, verify=True)
    except Exception:
        pass


def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 30,
    }

    if offset is not None:
        params["offset"] = offset

    try:
        response = requests.get(
            url,
            params=params,
            timeout=35,
            verify=True,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return {"ok": False, "result": []}


def is_valid_aadhaar(aadhaar_number):
    return (
        isinstance(aadhaar_number, str)
        and len(aadhaar_number) == 12
        and aadhaar_number.isdigit()
    )


def aadhaar_lookup(aadhaar_number):
    try:
        response = requests.get(
            EXTERNAL_API_URL,
            params={"aadhaar_no": aadhaar_number},
            timeout=30,
            verify=True,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def main():
    offset = None

    keyboard = {
        "keyboard": [
            [{"text": "🆔 Aadhaar to PAN"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
    }

    while True:
        try:
            updates = get_updates(offset)

            if not updates.get("ok"):
                time.sleep(2)
                continue

            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message")
                if not message:
                    continue

                chat = message.get("chat", {})
                chat_id = chat.get("id")

                if chat_id is None:
                    continue

                text = message.get("text", "")
                text = text.strip()

                if text == "/start":
                    send_message(
                        chat_id,
                        "👋 Welcome!\n\nSelect an option below.",
                        reply_markup=keyboard,
                    )

                elif text == "🆔 Aadhaar to PAN":
                    send_message(
                        chat_id,
                        "🪪 Send 12 digit Aadhaar Number:",
                    )

                elif is_valid_aadhaar(text):
                    result = aadhaar_lookup(text)

                    if result is None:
                        send_message(
                            chat_id,
                            "❌ API Error. Please try again later.",
                        )
                    else:
                        formatted = json.dumps(
                            result,
                            indent=4,
                            ensure_ascii=False,
                        )

                        send_message(
                            chat_id,
                            f"<pre>{formatted}</pre>",
                            parse_mode="HTML",
                        )

                else:
                    send_message(
                        chat_id,
                        "❌ Invalid Aadhaar Number. Please send a valid 12 digit Aadhaar Number.",
                    )

        except Exception:
            time.sleep(2)


if __name__ == "__main__":
    main()
