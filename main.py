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

SPREADSHEET_ID = "12nY7zYTpgBtdGPIjNo75OdY9iCid4ixEYwyuaKZWKVM"
sh = client.open_by_key(SPREADSHEET_ID)

users_sheet = sh.sheet1
conspect_sheet = sh.worksheet("9_conspect")
terms_sheet = sh.worksheet("9_termins")

TOKEN = "8290405338:AAF2jD1Ja1dsfpbMCYCybEMEnyVKw-KamxA"
bot = telebot.TeleBot(TOKEN)

authorized_users = set()
user_state = {}

@bot.message_handler(func=lambda m: m.text.endswith("класс"))
def choose_class(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in authorized_users:
        bot.send_message(chat_id, "Алдымен телефон нөмірін енгізіңіз.")
        return

    if text not in AVAILABLE_CLASSES:
        bot.send_message(
            chat_id,
            f"📘 {text} үшін материалдар әзірге дайын емес."
        )
        return

    user_state[chat_id] = {"class": "9"}

    # бөлімдер
    sections = list(set(conspect_sheet.col_values(2)[1:]))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for sec in sections:
        markup.add(sec)
    markup.add("⬅️ Назад")

    bot.send_message(
        chat_id,
        "📚 9 класс. Бөлімді таңдаңыз:",
        reply_markup=markup
    )
    @bot.message_handler(func=lambda m: m.text in conspect_sheet.col_values(2))
def choose_section(message):
    chat_id = message.chat.id
    section = message.text

    user_state[chat_id]["section"] = section

    records = conspect_sheet.get_all_records()
    conspects = [
        r["section"] for r in records
        if r["section"] == section
    ]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📄 Конспект")
    markup.add("⬅️ Назад")

    bot.send_message(
        chat_id,
        f"📘 {section}\nКонспектті таңдаңыз:",
        reply_markup=markup
    )
    @bot.message_handler(func=lambda m: m.text == "📄 Конспект")
def show_conspect(message):
    chat_id = message.chat.id
    section = user_state[chat_id]["section"]

    records = conspect_sheet.get_all_records()
    for r in records:
        if r["section"] == section:
            bot.send_message(chat_id, r["content"])
            break
            
bot.infinity_polling()
