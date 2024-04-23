from pprint import pprint
import telepot
import time
from docx2txt import get_docx_text
from wget import download
from os import system

def handle(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)

	answer = ''
	help = "Hi friend, I can read docx files for you.\n" \
		   "To start, just send me a docx file.\n" \
		   "I'll answer with the content of this file."
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
		answer = get_docx_text(downloaded_file_path)
		# if answer is empty, warn user
		if not answer:
			answer = "I'm sorry but I found nothing in this file."

		# delete used file
		system('rm -vf ' + downloaded_file_path)

	else:
		answer = "I'm sorry, I couldn't understand your command.\n" \
				 "Type /help to get some instructions."

	bot.sendMessage(chat_id, answer)

# instantiate bot
TOKEN = open('token.txt', 'r').read()
bot = telepot.Bot(TOKEN)
pprint(bot.getMe())

# handling messages
bot.message_loop(handle)
pprint('Listening ...')

# hanging program execution
while True:
	time.sleep(10)