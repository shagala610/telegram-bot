import telebot
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from telebot import types

creds_json = os.getenv("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(credentials)

sheet = client.open_by_key("Bot база").sheet1

TOKEN = "8290405338:AAF2jD1Ja1dsfpbMCYCybEMEnyVKw-KamxA"
bot = telebot.TeleBot(TOKEN)

authorized_users = set()

def find_user_by_phone(phone):
    records = sheet.get_all_records()
    for row in records:
        if str(row["phone"]) == phone:
            return row["name"]
    return None

def class_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("7 класс", "8 класс", "9 класс")
    kb.add("10 класс", "11 класс")
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "📱 Введите номер телефона (без +):\nПример: 87475620186",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda message: True)
def main_handler(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id in authorized_users:
        if text in ["7 класс", "8 класс", "9 класс", "10 класс", "11 класс"]:
            bot.send_message(
                chat_id,
                f"📚 Раздел «{text}» пока в разработке."
            )
        else:
            bot.send_message(chat_id, "Выберите класс кнопками 👇")
        return

    name = find_user_by_phone(text)

    if name:
        authorized_users.add(chat_id)
        bot.send_message(
            chat_id,
            f"Привет, {name} 👋\nВыберите класс:",
            reply_markup=class_keyboard()
        )
    else:
        bot.send_message(
            chat_id,
            "❌ Ваш номер отсутствует в базе.\n"
            "Обратитесь к администратору:\n"
            "+77745620186"
        )

bot.infinity_polling()
