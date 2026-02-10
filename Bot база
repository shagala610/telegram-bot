import telebot
import os
import json
import gspread
from google.oauth2.service_account import Credentials

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Google creds алу
creds_json = os.getenv("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(credentials)

sheet = client.open("Бот база").sheet1


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Телефон нөміріңізді жазыңыз (8XXXXXXXXXX форматта)")


@bot.message_handler(func=lambda message: True)
def check_phone(message):
    phone = message.text.strip()

    data = sheet.get_all_records()

    for row in data:
        if str(row["phone"]) == phone:
            name = row["name"]
            bot.send_message(message.chat.id, f"Сәлем {name} 👋")
            return

    bot.send_message(
        message.chat.id,
        "Сіздің номер базаға тіркелмеген.\nАдминге жазыңыз."
    )


bot.infinity_polling()
