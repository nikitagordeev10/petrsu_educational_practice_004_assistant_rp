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

import re
import pandas as pd
import docx

def get_docx_data(path):
    doc = docx.Document(path)
    full_text = []
    found = False
    data = []

    for paragraph in doc.paragraphs:
        if found:
            full_text.append(paragraph.text)
            match = re.match(r'^Ответственный: (.+)', paragraph.text)
            if match:
                responsible = match.group(1)
            match = re.match(r'^Срок: (.+)', paragraph.text)
            if match:
                date = match.group(1)
                data.append([task, responsible, date])
        elif re.match(r'^\s*\d+\.', paragraph.text):
            task = re.sub(r'^\s*\d+\.', '', paragraph.text).strip()
        elif re.match(r'^\s*РЕШИЛИ:', paragraph.text):
            found = True
            full_text.append(paragraph.text)

    df = pd.DataFrame(data, columns=['Задача', 'Ответственный', 'Дата'])
    return df


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

        # if answer is empty, warn user
        if answer_df.empty:
            bot.sendMessage(chat_id, "Извините, но этот файл пустой.")
        else:
            # Send data in chunks to avoid "text is too long" error
            answer_text = answer_df.to_string(index=False)
            for chunk in split_text(answer_text, chunk_size=3000):
                bot.sendMessage(chat_id, chunk)

        # delete used file
        system('rm -vf ' + downloaded_file_path)

    else:
        bot.sendMessage(chat_id, "Извините, я не смог понять вашу команду.\nВведите /help, чтобы получить инструкции.")

def split_text(text, chunk_size=3000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

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
