import telebot
import os
import json
import gspread
from google.oauth2.service_account import Credentials

creds_json = os.getenv("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(credentials)

sheet = client.open("Bot база").sheet1

TOKEN = "8290405338:AAF2jD1Ja1dsfpbMCYCybEMEnyVKw-KamxA"
bot = telebot.TeleBot(TOKEN)

authorized_users = set()

def find_user_by_phone(phone):
    records = sheet.get_all_records()
    for row in records:
        if str(row["phone"]) == phone:
            return row["name"]
    return None


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "📱 Напишите номер телефона")


@bot.message_handler(func=lambda message: True)
def check_phone(message):

    if not message.text:
        return

    phone = message.text.strip()

    name = find_user_by_phone(phone)

    if name:
        authorized_users.add(message.chat.id)

        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("9 класс", "10 класс")
        markup.add("7 класс", "8 класс", "11 класс")

        bot.send_message(message.chat.id,
                         f"Привет, {name} 👋\nВыберите класс:",
                         reply_markup=markup)

    else:
        bot.send_message(message.chat.id,
                         "❌ Ваш номер отсутствует в базе.\n"
                         "Обратитесь к администратору: +77745620186")


bot.infinity_polling()
