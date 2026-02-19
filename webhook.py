from flask import Flask, request
import telebot
import json
import os
import hmac
import hashlib
import random

TOKEN = os.getenv("8050976089:AAGaHpknsUTBL2jeuB5lq4laJhdN7-q-1tk")
ADMIN_ID = os.getenv("6658513478")
RAZOR_SECRET = os.getenv("singbotx_official")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

DB_FILE = "database.json"

# Save order to database
def save_order(order):
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

    data[str(order["order_id"])] = order

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Verify signature
def verify_signature(request):
    received_sig = request.headers.get("X-Razorpay-Signature")
    computed_sig = hmac.new(
        RAZOR_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(received_sig, computed_sig)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Signature verification
    if not verify_signature(request):
        return "Invalid signature", 400

    data = request.json

    if data['event'] == 'payment.captured':
        order_id = "SING" + str(random.randint(1000,9999))
        order = {
            "order_id": order_id,
            "status": "paid",
            "payment_id": data['payload']['payment']['entity']['id'],
            "amount": data['payload']['payment']['entity']['amount']/100
        }

        save_order(order)

        bot.send_message(
            ADMIN_ID,
            f"""
New Payment Received ✅

Order ID: {order_id}
Amount: ₹{order['amount']}
Payment ID: {order['payment_id']}
Status: Paid
"""
        )

    return "OK"

app.run(host="0.0.0.0", port=10000)
