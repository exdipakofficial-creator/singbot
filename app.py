from flask import Flask, request
import telebot
import os
import json
import hmac
import hashlib
import random

# Environment Variables
TOKEN = os.getenv("8050976089:AAGaHpknsUTBL2jeuB5lq4laJhdN7-q-1tk")
ADMIN_ID = int(os.getenv("6658513478"))
RAZOR_SECRET = os.getenv("singbotx_official")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

DB_FILE = "database.json"
user_plan = {}  # Temporary storage for UID input

# ---------------------------
# Database functions
# ---------------------------
def save_order(order):
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

    data[str(order["order_id"])] = order

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------------------
# Razorpay Signature Verify
# ---------------------------
def verify_signature(request):
    received_sig = request.headers.get("X-Razorpay-Signature")
    computed_sig = hmac.new(
        RAZOR_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(received_sig, computed_sig)

# ---------------------------
# Telegram commands (via webhook)
# ---------------------------
@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# ---------------------------
# Main Menu
# ---------------------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        "Shop Now 🛒", 
        "My Profile 👤",
        "Wallet 💰", 
        "Support 🆘",
        "My Orders 📦", 
        "Refer & Earn 🎁",
        "Packages / Plan List 🛍️"
    )
    bot.send_message(message.chat.id, "Welcome to SING IS LIVE X Bot! Choose an option below:", reply_markup=markup)

# ---------------------------
# Individual Menu Handlers
# ---------------------------
@bot.message_handler(func=lambda message: message.text == "Shop Now 🛒")
def shop_now(message):
    bot.send_message(message.chat.id, "Available Plans:\n1. 249 Plan\n2. 499 Plan\n3. 999 Plan")

@bot.message_handler(func=lambda message: message.text == "My Profile 👤")
def profile(message):
    bot.send_message(message.chat.id, f"Your profile:\nName: User\nChat ID: {message.chat.id}")

@bot.message_handler(func=lambda message: message.text == "Wallet 💰")
def wallet(message):
    bot.send_message(message.chat.id, "Wallet Balance: ₹0.00")

@bot.message_handler(func=lambda message: message.text == "Support 🆘")
def support(message):
    bot.send_message(message.chat.id, "Contact support: support@example.com")

@bot.message_handler(func=lambda message: message.text == "My Orders 📦")
def my_orders(message):
    bot.send_message(message.chat.id, "You have 0 orders")

@bot.message_handler(func=lambda message: message.text == "Refer & Earn 🎁")
def refer(message):
    bot.send_message(message.chat.id, "Share this link to earn rewards:\nhttps://t.me/SINGISLIVEXBot?start=ref123")

# ---------------------------
# Plan Selection Workflow
# ---------------------------
@bot.message_handler(func=lambda message: message.text == "Packages / Plan List 🛍️")
def plans(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("249 Plan")
    markup.add("499 Plan")
    markup.add("999 Plan")
    bot.send_message(message.chat.id, "Select Your Plan:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["249 Plan","499 Plan","999 Plan"])
def ask_uid(message):
    user_plan[message.chat.id] = message.text
    bot.send_message(message.chat.id, "ENTER YOUR GUILD UID:")

@bot.message_handler(func=lambda message: message.chat.id in user_plan)
def get_uid(message):
    plan = user_plan[message.chat.id]
    markup = telebot.types.InlineKeyboardMarkup()
    
    # Plan → Payment link
    if plan == "249 Plan":
        link = "https://rzp.io/rzp/DKa3CHU"
    elif plan == "499 Plan":
        link = "https://rzp.io/rzp/VBe8tXm"
    else:
        link = "https://rzp.io/rzp/09HoqO5A"

    pay = telebot.types.InlineKeyboardButton("PAY NOW", url=link)
    markup.add(pay)

    bot.send_message(
        message.chat.id,
        f"""
Confirm Order

Plan: {plan}
Guild UID: {message.text}

Click PAY NOW
""",
        reply_markup=markup
    )
    user_plan.pop(message.chat.id)

# ---------------------------
# Razorpay Webhook
# ---------------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    if not verify_signature(request):
        return "Invalid signature", 400

    data = request.json

    if data.get('event') == 'payment.captured':
        order_id = "SING" + str(random.randint(1000,9999))
        payment = data['payload']['payment']['entity']
        order = {
            "order_id": order_id,
            "status": "paid",
            "payment_id": payment['id'],
            "amount": payment['amount']/100
        }

        save_order(order)

        # Notify admin
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

# ---------------------------
# Run Flask App
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
