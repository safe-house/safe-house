import requests

TELEGRAM_URL = "https://api.telegram.org/bot"
BOT_TOKEN = "970539780:AAElJ4Gr1-BBcmBKHAL31yVg-SLYebt8Km8"


def send_message(message, chat_id):
    data = {
        "chat_id": chat_id,
        "text": message,

    }
    print(chat_id, message)
    response = requests.post(
        TELEGRAM_URL + BOT_TOKEN + "/sendMessage", data=data
    )