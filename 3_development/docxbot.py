from pprint import pprint
import telepot
import time
from wget import download
from os import system
import docx
import io
import pandas as pd

def get_docx_text(path):
    content = '\n'.join([p.text for p in docx.Document(path).paragraphs])
    df = pd.read_csv(io.StringIO(content))
    return df


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    answer = ''
    help = "Здравствуйте, я могу структурировать информацию по вашим проектам.\n" \
           "Пришлите мне протокол совещаний в формате docx.\n" \
           "Я изучу его и составлю Вам майнд-карту."
    if content_type == 'text' and\
            ('/start' in msg['text'] or '/help' in msg['text']):
        answer = help
    elif content_type == 'document':
        # generate file url
        file_id = msg['document']['file_id']
        file_path = bot.getFile(file_id)['file_path']
        file_url = 'https://api.telegram.org/file/bot' + TOKEN + '/' + file_path

        # download and store file in subdir
        output_path = './temp/'
        downloaded_file_path = download(file_url, out=output_path)
        file_name = msg['document']['file_name']

        # open file and get ASCII data
        answer_df = get_docx_text(downloaded_file_path)
        # if answer is empty, warn user
        if answer_df.empty:
            answer = "Извините, но этот файл пустой."
        else:
            answer = answer_df.to_string(index=False)

        # delete used file
        system('rm -vf ' + downloaded_file_path)

    else:
        answer = "Извините, я не смог понять вашу команду.\n" \
                 "Введите /help, чтобы получить инструкции."

    bot.sendMessage(chat_id, answer)

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
