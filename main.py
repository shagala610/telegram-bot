import telebot
import os
import json
import gspread
from telebot import types
from google.oauth2.service_account import Credentials

creds_json = os.getenv("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(credentials)

sheet = client.open_by_key("12nY7zYTpgBtdGPIjNo75OdY9iCid4ixEYwyuaKZWKVM").sheet1

TOKEN = os.getenv("8290405338:AAF2jD1Ja1dsfpbMCYCybEMEnyVKw-KamxA")
bot = telebot.TeleBot(TOKEN)

authorized_users = {}

def find_user_by_phone(phone):
    records = sheet.get_all_records()
    for row in records:
        if str(row["phone"]) == phone:
            return row["name"]
    return None

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "📱 Введите номер телефона:")

@bot.message_handler(func=lambda message: message.chat.id not in authorized_users)
def check_phone(message):
    phone = message.text.strip()
    name = find_user_by_phone(phone)

    if name:
        authorized_users[message.chat.id] = name

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("7 класс", "8 класс")
        markup.add("9 класс", "10 класс", "11 класс")

        bot.send_message(
            message.chat.id,
            f"✅ Добро пожаловать, {name}!\n\nВыберите класс:",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ Ваш номер отсутствует в базе.\nОбратитесь к администратору: +77475620186"
        )

@bot.message_handler(func=lambda message: message.chat.id in authorized_users)
def handle_classes(message):

    if message.text == "9 класс":
        bot.send_message(message.chat.id,
                         "📘 9 класс\n\nВыберите раздел:\n- Конспект\n- Основные понятия\n- Тест\n- Доп. материал")

    elif message.text in ["7 класс", "8 класс", "10 класс", "11 класс"]:
        bot.send_message(message.chat.id,
                         f"📚 Раздел {message.text} пока в разработке.")

    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите класс из кнопок.")

bot.infinity_polling()
