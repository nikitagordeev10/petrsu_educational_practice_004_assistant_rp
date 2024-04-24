from libraries import *
from password import *
from backend import *
TOKEN = open('token.txt', 'r').read()
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    help_text = "Я могу структурировать информацию по вашим проектам.\n" \
                "Пришлите мне протокол совещаний в формате docx.\n" \
                "Я изучу его и составлю Вам майнд-карту."
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    bot.send_message(user_id, f"Привет, {user_name}!")
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['homepage'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    button_view_uploaded_document = types.InlineKeyboardButton('Посмотреть ранее загруженный документ',
                                                       callback_data='view_uploaded_document')
    button_upload_a_new_document = types.InlineKeyboardButton('Загрузить новый документ',
                                                       callback_data='upload_a_new_document')
    markup.row(button_view_uploaded_document)
    markup.row(button_upload_a_new_document)
    homepage_text = "Если вы загружали документ раньше, можете работать с ним.\n" \
                "Если вы загрузите новый  документ, то данные о старом удалятся."
    bot.send_message(message.chat.id, homepage_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'upload_a_new_document')
def upload_new_document(call):
    bot.send_message(call.message.chat.id, "Пожалуйста, загрузите новый документ")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    markup = types.InlineKeyboardMarkup()
    button_report_project = types.InlineKeyboardButton('Сформировать отчёт "По проектам"',
                                                       callback_data='report_project')
    button_report_responsible = types.InlineKeyboardButton('Сформировать отчёт "По ответственным"',
                                                           callback_data="report_responsible")
    button_report_dates = types.InlineKeyboardButton('Сформировать отчёт "По датам"', callback_data="report_dates")
    markup.row(button_report_project)
    markup.row(button_report_responsible)
    markup.row(button_report_dates)
    bot.reply_to(message, 'Окей, вот что я могу сделать с документом', reply_markup=markup)

    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'

    output_path = './temp/'
    downloaded_file_path = download(file_url, out=output_path)

    process_document(message, downloaded_file_path)

@bot.message_handler(func=lambda message: True)
def handle_other(message):
    bot.send_message(message.chat.id, "Извините, я не смог понять вашу команду.\nВведите /help, чтобы получить инструкции.")

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)

bot.polling(none_stop=True)
