from libraries import *
import json

def separate_messages_for_telegram(result_lines):
    telegram_text = ""
    first_task = True

    for task in result_lines:
        telegram_text += "<b>Задача:</b> " + task["task"] + "\n"
        telegram_text += "---\n"
        telegram_text += "<b>Ответственный:</b> " + task["task_executor"] + "\n"
        telegram_text += "---\n"
        telegram_text += "<b>Срок:</b> " + task["deadline"] + "\n"
        telegram_text += "---\n"
        telegram_text += "<b>Статус:</b> " + task["state"] + "\n"
        telegram_text += "---\n"
        telegram_text += "<b>Комментарий:</b> " + task["comment"] + "\n"
        telegram_text += "<button>\n"
        telegram_text += "\n"

    return telegram_text

# Пример использования
with open("from_db.json", "r", encoding="windows-1251") as file:
    data = json.load(file)

telegram_message = separate_messages_for_telegram(data)
print(telegram_message)

