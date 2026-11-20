import os
import requests
from flask import Flask, request
from google import genai

app = Flask(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_token_123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")


@app.route("/", methods=["GET"])
def home():
    return "Instagram AI Agent is running!", 200


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # التحقق من الربط مع Meta
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    # استقبال الرسائل والرد عليها
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        print("Incoming webhook POST:", data, flush=True)

        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for messaging in entry.get("messaging", []):
                    sender_id = messaging.get("sender", {}).get("id")
                    message_obj = messaging.get("message", {})
                    message_text = message_obj.get("text")
                    is_echo = message_obj.get("is_echo", False)

                    if sender_id and message_text and not is_echo:
                        try:
                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=(
                                    "أنت مساعد مبيعات ذكي ومحترف لمتجر على إنستغرام. "
                                    f"أجب باختصار ولباقة على رسالة العميل التالية: {message_text}"
                                ),
                            )
                            reply_text = (response.text or "").strip()
                            if reply_text:
                                send_instagram_message(sender_id, reply_text)
                        except Exception as e:
                            print("Error generating or sending reply:", e, flush=True)

        return "EVENT_RECEIVED", 200


def send_instagram_message(recipient_id, text):
    url = "https://graph.instagram.com/v21.0/me/messages"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
    }
    res = requests.post(url, headers=headers, json=payload, timeout=15)
    print("Instagram send status:", res.status_code, res.text, flush=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_token_123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Instagram AI Agent is running!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # التحقق من الربط مع Meta
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    # استقبال الرسائل والرد عليها
    if request.method == "POST":
        data = request.json
        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for messaging in entry.get("messaging", []):
                    sender_id = messaging.get("sender", {}).get("id")
                    message_text = messaging.get("message", {}).get("text")
                    
                    if message_text and not messaging.get("message", {}).get("is_echo"):
                        # توليد الرد عبر Gemini
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=f"أنت مساعد مبيعات ذكي ومحترف لمتجر على إنستغرام. أجب باختصار ولباقة على رسالة العميل التالية: {message_text}",
                        )
                        send_instagram_message(sender_id, response.text)
        return "EVENT_RECEIVED", 200

def send_instagram_message(recipient_id, text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
