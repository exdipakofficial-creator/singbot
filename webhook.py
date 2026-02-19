from flask import Flask, request
import telebot
import json
import random

TOKEN = "8050976089:AAGaHpknsUTBL2jeuB5lq4laJhdN7-q-1tk"
ADMIN_ID = "6658513478"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def save_order(order):
    with open("database.json","r") as f:
        data = json.load(f)

    data[str(order["order_id"])] = order

    with open("database.json","w") as f:
        json.dump(data,f,indent=4)

@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

    if data['event'] == 'payment.captured':

        order_id = "SING" + str(random.randint(1000,9999))

        order = {
            "order_id": order_id,
            "status": "paid"
        }

        save_order(order)

        bot.send_message(
            ADMIN_ID,
            f"""
New Payment Received

Order ID: {order_id}
Status: Paid
"""
        )

    return "OK"

app.run(host="0.0.0.0", port=10000)
