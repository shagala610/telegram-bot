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

AVAILABLE_CLASSES = ["9 класс"]

# ===== ПОИСК ПОЛЬЗОВАТЕЛЯ ПО ТЕЛЕФОНУ =====
def find_user_by_phone(phone):
    records = users_sheet.get_all_records()
    for row in records:
        if str(row["phone"]) == phone:
            return row["name"]
    return None


# ===== КЛАВИАТУРА ВЫБОРА КЛАССА =====
def class_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("7 класс", "8 класс", "9 класс")
    kb.add("10 класс", "11 класс")
    return kb


# ===== КЛАВИАТУРА 9 КЛАССА =====
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


# ===== ПОЛУЧЕНИЕ КОНТЕНТА ИЗ SHEET =====
def get_content(sheet, section_name):
    rows = sheet.get_all_records()
    for row in rows:
        if row["section"] == section_name:
            return row["content"]
    return "📘 Материал пока не добавлен."


# ===== START =====
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "📱 Введите номер телефона (без +):\nПример: 87475620186",
        reply_markup=types.ReplyKeyboardRemove()
    )


# ===== ОСНОВНОЙ HANDLER =====
@bot.message_handler(func=lambda message: message.text.isdigit())
def check_user(message):
    chat_id = message.chat.id
    phone = message.text.strip()

    name = find_user_by_phone(phone)
    if not name:
        bot.send_message(
            chat_id,
            "❌ Сіздің нөміріңіз базаға тіркелмеген.\n"
            "Әкімшіге хабарласыңыз:\n+77745620186"
        )
        return

    authorized_users.add(chat_id)
    user_state[chat_id] = {}

    bot.send_message(
        chat_id,
        f"Привет, {name} 👋\nВыберите класс:",
        reply_markup=class_keyboard()
    )
    # --- ВЫБОР КЛАССА ---
    if text.endswith("класс"):
        if text not in AVAILABLE_CLASSES:
            bot.send_message(
                chat_id,
                f"📘 Материалы для {text} пока в разработке.\n"
                "В данный момент доступен только 9 класс.",
                reply_markup=class_keyboard()
            )
            return

        user_state[chat_id]["class"] = "9 класс"

        bot.send_message(
            chat_id,
            "📘 9 класс. Выберите раздел:",
            reply_markup=nine_class_keyboard()
        )
        return

    # --- НАЗАД ---
    if text == "⬅️ Назад":
        bot.send_message(
            chat_id,
            "Выберите класс:",
            reply_markup=class_keyboard()
        )
        return

    # --- РАЗДЕЛЫ 9 КЛАССА ---
    if user_state.get(chat_id, {}).get("class") == "9 класс":
        content = get_content(conspect_sheet, text)
        bot.send_message(chat_id, content)
        return

    # --- НА ВСЯКИЙ СЛУЧАЙ ---
    bot.send_message(
        chat_id,
        "Пожалуйста, выберите вариант кнопками 👇"
    )

bot.infinity_polling()
