from pprint import pprint
import telepot
import time
from wget import download
from os import system
import docx
import io
import pandas as pd
from telegram.ext import Updater, MessageHandler
import re

import re
import pandas as pd


def process_text(text):
    """Process text to extract tasks, responsible persons, and dates."""
    tasks = []
    responsible = ""
    deadline = ""
    start_processing = False
    for line in text.split('\n'):
        if start_processing:
            if line.strip():
                match_responsible = re.match(r'^Ответственный: (.+)', line)
                match_date = re.match(r'^\s*Срок: (.+)', line)
                if match_responsible:
                    responsible = match_responsible.group(1)
                elif match_date:
                    deadline = match_date.group(1)
                else:
                    tasks.append([line.strip(), responsible, deadline])
        elif line.startswith('В части Проекта'):
            tasks.append(['В части Проекта:', '', ''])  # полная строка
            start_processing = True
    return pd.DataFrame(tasks, columns=['Задача', 'Ответственный', 'Дата'])


def get_docx_data(path):
    """Выводит обработанный текст в виде таблички"""
    doc = docx.Document(path)
    full_text = ""
    tables = []
    found = False
    for paragraph in doc.paragraphs:
        if found:
            if paragraph.text.startswith('В части Проекта'):
                tables.append(process_text(full_text))
                full_text = ""
            full_text += paragraph.text + '\n'
        elif re.match(r'^\s*РЕШИЛИ:', paragraph.text):
            found = True
            full_text += paragraph.text + '\n'
    # Добавляем последнюю таблицу
    tables.append(process_text(full_text))
    return pd.concat(tables, ignore_index=True)


import pandas as pd
import re

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    help_text = "Здравствуйте, я могу структурировать информацию по вашим проектам.\n" \
                "Пришлите мне протокол совещаний в формате docx.\n" \
                "Я изучу его и составлю Вам майнд-карту."

    if content_type == 'text' and ('/start' in msg['text'] or '/help' in msg['text']):
        bot.sendMessage(chat_id, help_text)
        return

    if content_type == 'document':
        # generate file url
        file_id = msg['document']['file_id']
        file_path = bot.getFile(file_id)['file_path']
        file_url = 'https://api.telegram.org/file/bot' + TOKEN + '/' + file_path

        # download and store file in subdir
        output_path = './temp/'
        downloaded_file_path = download(file_url, out=output_path)
        file_name = msg['document']['file_name']

        # open file and get ASCII data
        answer_df = get_docx_data(downloaded_file_path)

        # Drop empty rows
        answer_df = answer_df.dropna()

        # Remove leading tabs and extra spaces from each cell
        answer_df = answer_df.apply(lambda x: x.map(lambda y: re.sub(r'^\s+|\s+$', '', y, flags=re.M)))


        # Combine rows into one string
        answer_text = answer_df.apply(lambda row: ' '.join(row), axis=1)

        # Remove empty lines
        answer_text = answer_text[answer_text != '']

        # if answer is empty, warn user
        if answer_text.empty:
            bot.sendMessage(chat_id, "Извините, но этот файл пустой.")
        else:
            # Send data in chunks to avoid "text is too long" error
            for chunk in split_text('\n'.join(answer_text), chunk_size=3000):
                bot.sendMessage(chat_id, chunk)

        # delete used file
        system('rm -vf ' + downloaded_file_path)

    else:
        bot.sendMessage(chat_id, "Извините, я не смог понять вашу команду.\nВведите /help, чтобы получить инструкции.")






def split_text(text, chunk_size=3000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


# instantiate bot
TOKEN = open('token.txt', 'r').read()
bot = telepot.Bot(TOKEN)
pprint(bot.getMe())

# handling messages
bot.message_loop(handle)
pprint('Слушаю ...')

# hanging program execution
while True:
    time.sleep(10)
