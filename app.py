import os
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# تهيئة عميل جيمناي باستخدام مفتاح API
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "Instagram AI Agent is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    # استدعاء جيمناي لتوليد الرد للعميل
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="أجب باختصار كمساعد مبيعات لمتجر",
    )
    return jsonify({"status": "success", "reply": response.text}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
