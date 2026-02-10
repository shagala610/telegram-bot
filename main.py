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

users_sheet = client.open_by_key(
    "12nY7zYTpgBtdGPIjNo75OdY9iCid4ixEYwyuaKZWKVM"
).sheet1

conspect_sheet = client.open_by_key(
    "12n7zYTpgBtdGPIjNo75OdY9iCid4ixEYwyaKZWkVM"
).worksheet("9_conspect")
terms_sheet = client.open_by_key(12nY7zYTpgBtdGPIjNo75OdY9iCid4ixEYwyuaKZWKVM).worksheet("9_termins")

TOKEN = "8290405338:AAF2jD1Ja1dsfpbMCYCybEMEnyVKw-KamxA"
bot = telebot.TeleBot(TOKEN)

authorized_users = set()
user_state = {}

def find_user_by_phone(phone):
    records = users_sheet.get_all_records()
    for row in records:
        if str(row["phone"]) == phone:
            return row["name"]
    return None

def class_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("7 класс", "8 класс", "9 класс")
    kb.add("10 класс", "11 класс")
    return kb

def nine_class_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Клеточная биология")
    kb.add("Многообразие живых организмов")
    kb.add("Влияние деятельности человека")
    kb.add("Питание", "Транспорт веществ")
    kb.add("Дыхание", "Выделение")
    kb.add("Координация и регуляция")
    kb.add("Движение")
    kb.add("Молекулярная биология")
    kb.add("Клеточный цикл")
    kb.add("Наследственность и изменчивость")
    kb.add("Рост и развитие")
    kb.add("Размножение")
    kb.add("Эволюция")
    kb.add("⬅️ Назад")
    return kb

def section_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📘 Конспект", "📚 Термины")
    kb.add("⬅️ Назад")
    return kb

def get_content(sheet, section_name):
    rows = sheet.get_all_records()
    for row in rows:
        if row["section"] == section_name:
            return row["content"]
    return "Материал пока не добавлен."

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

    if chat_id not in authorized_users:
        name = find_user_by_phone(text)
        if name:
            authorized_users.add(chat_id)
            user_state[chat_id] = {}
            bot.send_message(
                chat_id,
                f"Привет, {name} 👋\nВыберите класс:",
                reply_markup=class_keyboard()
            )
        else:
            bot.send_message(
                chat_id,
                "❌ Ваш номер отсутствует в базе.\nОбратитесь к администратору:\n+77745620186"
            )
        return

    if text == "9 класс":
        user_state[chat_id]["class"] = 9
        bot.send_message(
            chat_id,
            "📘 9 класс. Выберите раздел:",
            reply_markup=nine_class_keyboard()
        )
        return

    if text == "⬅️ Назад":
        if "section" in user_state.get(chat_id, {}):
            user_state[chat_id].pop("section", None)
            bot.send_message(
                chat_id,
                "📘 Выберите раздел:",
                reply_markup=nine_class_keyboard()
            )
        else:
            bot.send_message(
                chat_id,
                "Выберите класс:",
                reply_markup=class_keyboard()
            )
        return

    sections = [
        "Клеточная биология",
        "Многообразие живых организмов",
        "Влияние деятельности человека",
        "Питание",
        "Транспорт веществ",
        "Дыхание",
        "Выделение",
        "Координация и регуляция",
        "Движение",
        "Молекулярная биология",
        "Клеточный цикл",
        "Наследственность и изменчивость",
        "Рост и развитие",
        "Размножение",
        "Эволюция"
    ]

    if text in sections:
        user_state[chat_id]["section"] = text
        bot.send_message(
            chat_id,
            f"Раздел: {text}\nВыберите формат:",
            reply_markup=section_keyboard()
        )
        return

    if text == "📘 Конспект":
        section = user_state[chat_id].get("section")
        content = get_content(conspect_sheet, section)
        bot.send_message(chat_id, content)
        return

    if text == "📚 Термины":
        section = user_state[chat_id].get("section")
        content = get_content(terms_sheet, section)
        bot.send_message(chat_id, content)
        return

    bot.send_message(chat_id, "Выберите вариант кнопками 👇")

bot.infinity_polling()
