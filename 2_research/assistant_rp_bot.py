from libraries import *
from document_processing import *

def split_text(text, chunk_size=3000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


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
        output_path = '../3_development/temp/'
        downloaded_file_path = download(file_url, out=output_path)
        file_name = msg['document']['file_name']

        # open file and get ASCII data
        answer_df = all_text(downloaded_file_path)

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





# instantiate bot
TOKEN = open('../3_development/token.txt', 'r').read()
bot = telepot.Bot(TOKEN)
pprint(bot.getMe())

# handling messages
bot.message_loop(handle)
pprint('Слушаю ...')

# hanging program execution
while True:
    time.sleep(10)
