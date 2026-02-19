import telebot
from telebot import types

TOKEN =" 8050976089:AAGaHpknsUTBL2jeuB5lq4laJhdN7-q-1tk"

bot = telebot.TeleBot(TOKEN)

user_plan = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Packages / Plan List 🛍️")
    bot.send_message(message.chat.id, "Welcome to SING IS LIVE X Bot", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Packages / Plan List 🛍️")
def plans(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("249 Plan")
    markup.add("499 Plan")
    markup.add("999 Plan")
    bot.send_message(message.chat.id, "Select Plan:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["249 Plan","499 Plan","999 Plan"])
def ask_uid(message):
    user_plan[message.chat.id] = message.text
    bot.send_message(message.chat.id, "ENTER YOUR GUILD UID:")

@bot.message_handler(func=lambda message: message.chat.id in user_plan)
def get_uid(message):

    plan = user_plan[message.chat.id]

    markup = types.InlineKeyboardMarkup()

    if plan == "249 Plan":
        link = "https://rzp.io/rzp/DKa3CHU"
    elif plan == "499 Plan":
        link = "https://rzp.io/rzp/VBe8tXm"
    else:
        link = "https://rzp.io/rzp/09HoqO5A"

    pay = types.InlineKeyboardButton("PAY NOW", url=link)
    markup.add(pay)

    bot.send_message(
        message.chat.id,
        f"""
Confirm Order

Plan: {plan}
UID: {message.text}

Click PAY NOW
""",
        reply_markup=markup
    )

    user_plan.pop(message.chat.id)

bot.polling()
