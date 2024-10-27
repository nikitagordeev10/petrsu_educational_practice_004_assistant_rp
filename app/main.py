from libraries import *
from config import TG_TOKEN

bot = telebot.TeleBot(TG_TOKEN)

FILE_ID = None
FILE_INFO = None
FILE_URL = None

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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_view_uploaded_document = types.KeyboardButton('Посмотреть ранее загруженный документ')
    button_upload_a_new_document = types.KeyboardButton('Загрузить новый документ')
    markup.add(button_view_uploaded_document, button_upload_a_new_document)
    homepage_text = "Если вы загружали документ раньше, можете работать с ним.\n" \
                "Если вы загрузите новый  документ, то данные о старом удалятся."
    bot.send_message(message.chat.id, homepage_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Посмотреть ранее загруженный документ')
def view_uploaded_document(message):
    bot.send_message(message.chat.id, "Ранее загруженных документов не найдено")
    bot.send_message(message.chat.id, "Пожалуйста, загрузите новый документ")

@bot.message_handler(func=lambda message: message.text == 'Загрузить новый документ')
def upload_new_document(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, "Пожалуйста, загрузите новый документ", reply_markup=markup)


@bot.message_handler(content_types=['document'])
def handle_document(message):
    global FILE_ID, FILE_INFO, FILE_URL
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_report_project = types.KeyboardButton('Сформировать отчёт "По проектам"')
    button_report_responsible = types.KeyboardButton('Сформировать отчёт "По ответственным"')
    button_report_dates = types.KeyboardButton('Сформировать отчёт "По датам"')
    markup.add(button_report_project, button_report_responsible, button_report_dates)
    bot.reply_to(message, 'Окей, вот что я могу сделать с документом', reply_markup=markup)

    FILE_ID = message.document.file_id
    FILE_INFO = bot.get_file(FILE_ID)
    FILE_URL = f'https://api.telegram.org/file/bot{TG_TOKEN}/{FILE_INFO.file_path}'

@bot.message_handler(func=lambda message: message.text == 'Сформировать отчёт "По проектам"')
def report_project_callback(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_all_projects = types.KeyboardButton('Все проекты')
    button_commodus = types.KeyboardButton('Коммод')
    button_asu_eto = types.KeyboardButton('АСУ ЭТО и АСУ ТМО')
    button_tpir = types.KeyboardButton('ТПИР')
    markup.add(button_all_projects, button_commodus, button_asu_eto, button_tpir)
    bot.send_message(message.chat.id, "По каким проектам нужен отчёт?", reply_markup=markup)

    global FILE_ID, FILE_INFO, FILE_URL
    if FILE_ID and FILE_INFO and FILE_URL:
        output_path = './temp/'
        downloaded_file_path = download(FILE_URL, out=output_path)
        create_report_projects(message, downloaded_file_path)
    else:
        bot.send_message(message.chat.id, "Ошибка: файл не найден.")
def convert_docx_to_txt(file_path):
    document = Document(file_path)
    text = "\n".join([para.text for para in document.paragraphs])
    return text

def save_text_after_keyword(text, keyword):
    start_index = text.find(keyword)
    if start_index != -1:
        text = text[start_index + len(keyword):]
    return text

def clean_text(text):
    text = re.sub(r'\n{2,}', '\n', text)
    return text

def adding_keys_to_source_text(text):
    lines = text.split('\n')
    result_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("В части Проекта"):
            result_lines.append("Проект: " + line)
            i += 1
            if i < len(lines) and lines[i].strip().startswith("Ответственный:"):
                pass
            elif (i + 1 < len(lines) and
                  not lines[i+1].strip().startswith("Ответственный:")):
                result_lines.append("Подпроект: " + lines[i].strip())
                i += 1
                result_lines.append("Задача: " + lines[i].strip())
            elif i < len(lines) and not lines[i].strip().startswith("Ответственный:"):
                result_lines.append("Задача: " + lines[i].strip())

        elif line.startswith("Срок"):
            result_lines.append(line)
            i += 1
            if i < len(lines) and lines[i].strip().startswith("В части Проекта"):
                continue
            elif i < len(lines) and not lines[i].strip().startswith("Ответственный:"):
                next_line = lines[i].strip()
                if (i + 1 < len(lines) and
                    not lines[i+1].strip().startswith("Ответственный:")):
                    result_lines.append("Подроект: " + next_line)
                    i += 1
                    result_lines.append("Задача: " + lines[i].strip())
                else:
                    result_lines.append("Задача: " + next_line)

        elif line.startswith("Ответственный:"):
            result_lines.append(line)

        else:
            result_lines.append(line)

        i += 1

    if result_lines:
        result_lines.pop()  # Удаление последней строки, если список не пустой

    return result_lines


def add_status_and_comment(text):
    lines = text
    result_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Срок"):
            result_lines.append(line)
            result_lines.append("Статус: не сделано")
            result_lines.append("Комментарий: нет")
            result_lines.append("Руководитель: Е.С. Литвинов")
            i += 1
        else:
            result_lines.append(line)
            i += 1

    with open("text.txt", "w") as file:
        file.write('\n'.join(result_lines))

    return result_lines


def upload_to_database(text):
    pass

def reading_from_database(text):
    # with closing(psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST, port=PORT)) as conn:
    #     with conn.cursor() as cursor:
    #         cursor.execute("INSERT INTO task (task_creator_id, task_executor_id, task_name, subtack_name, task_description, created_at, deadline, state, comment) VALUES (:task_creator_id, :task_executor)")
    #         for row in cursor:
    #             print(row[0])
    pass


def separate_messages_for_telegram(result_lines):
    telegram_text = ""
    first_project = True

    for line in result_lines:
        line = line.strip()
        if line.startswith("Проект:"):
            if first_project:
                telegram_text += f"{line}\n"
                first_project = False
            else:
                telegram_text += f"<br>{line}\n"
        elif line.startswith("Задача:"):
            telegram_text += f"<br>{line}\n"
            telegram_text += "---\n"
        elif line.startswith("Ответственный:"):
            telegram_text += f"{line}\n"
            telegram_text += "---\n"
        elif line.startswith("Срок:"):
            telegram_text += f"{line}\n"
            telegram_text += "---\n"
        elif line.startswith("Статус:"):
            telegram_text += f"{line}\n"
            telegram_text += "---\n"
        elif line.startswith("Комментарий:"):
            telegram_text += f"{line}\n"
            telegram_text += "<button>\n"
        else:
            telegram_text += f"{line}\n"

    return telegram_text

def create_report_projects(message, file_path):
    text = convert_docx_to_txt(file_path)
    text = save_text_after_keyword(text, "РЕШИЛИ:")
    text = clean_text(text)
    result_lines = adding_keys_to_source_text(text)
    result_lines = add_status_and_comment(result_lines)
    telegram_text = separate_messages_for_telegram(result_lines)

    if telegram_text.strip() == "":
        bot.send_message(message.chat.id, "Извините, но этот файл пустой.")
    else:
        for line in telegram_text.split('<br>'):
            if '<button>' in line:
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text="Редактировать", callback_data="edit"))
                bot.send_message(message.chat.id, re.sub(r'<button>', '', line), reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, line)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "edit":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Задача')
        button2 = types.KeyboardButton('Ответственный')
        button3 = types.KeyboardButton('Срок')
        button4 = types.KeyboardButton('Статус')
        button5 = types.KeyboardButton('Комментарии')
        markup.add(button1, button2, button3, button4, button5)
        bot.send_message(call.message.chat.id, 'Какую информацию вы хотите изменить?', reply_markup=markup)

#
# @bot.callback_query_handler(func=lambda call: call.data == 'report_project')
# def report_project_callback(call):
#     global FILE_ID, FILE_INFO, FILE_URL
#     if FILE_ID and FILE_INFO and FILE_URL:
#         output_path = './temp/'
#         downloaded_file_path = download(FILE_URL, out=output_path)
#         create_report_projects(call.message, downloaded_file_path)
#     else:
#         bot.send_message(call.message.chat.id, "Ошибка: файл не найден.")



@bot.message_handler(func=lambda message: True)
def handle_other(message):
    bot.send_message(message.chat.id, "Извините, я не смог понять вашу команду.\n"
                                      "Введите /help, чтобы получить инструкции.")

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)

bot.polling(none_stop=True)
