from libraries import *
from dbpswd import *
TOKEN = open('token.txt', 'r').read()
bot = telebot.TeleBot(TOKEN)

FILE_ID = None
FILE_INFO = None
FILE_URL = None

# ############ backend ############

def split_text(text, chunk_size=3000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def all_text(path):
    doc = docx.Document(path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    df = pd.DataFrame(full_text, columns=['Text'])
    return df

def process_text(text):
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
                    deadline = match_date.group(1)  # Запоминаем дату
                else:
                    tasks.append([line.strip(), responsible, deadline])
        elif line.startswith('В части Проекта'):
            start_processing = True

    return pd.DataFrame(tasks, columns=['Задача', 'Ответственный', 'Дата'])

def get_docx_data(path):
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

    tables.append(process_text(full_text))

    return pd.concat(tables, ignore_index=True)

# ----------------------------------

def convert_docx_to_txt(docx_filepath, txt_filepath):
    document = Document(docx_filepath)
    with codecs.open(txt_filepath, 'w', "utf-8-sig") as o_file:
        for para in document.paragraphs:
            text = re.sub(r'\n{2,}', '\n', para.text)
            o_file.write(text + '\n')

# Удаляем весь текст до части "РЕШИЛИ"
def save_text_after_keyword(input_file, keyword, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    found = False
    text_after_keyword = []

    for line in lines:
        if found:
            text_after_keyword.append(line)
        elif keyword in line:
            found = True

    with open(output_file, 'w') as f:
        f.writelines(text_after_keyword)

def clean_text(input_file, output_file):
    # Читаем содержимое файла
    with open(input_file, 'r') as file:
        text = file.read()

    # Заменяем два и более переноса строк на один
    text = re.sub(r'\n{2,}', '\n', text)

    # Записываем измененный текст обратно в файл
    with open(output_file, 'w') as file:
        file.write(text)

def adding_keys_to_source_text(file_path, output_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line.startswith("В части Проекта"):
                output_file.write("Проект: " + line + "\n")
                i += 1
                if i < len(lines) and lines[i].strip().startswith("Ответственный:"):
                    # Нет дополнительных строк между
                    pass
                elif (i + 1 < len(lines) and
                      not lines[i+1].strip().startswith("Ответственный:")):
                    # Две строки до "Ответственный:"
                    output_file.write("Подпроект: " + lines[i].strip() + "\n")
                    i += 1
                    output_file.write("Задача: " + lines[i].strip() + "\n")
                elif i < len(lines) and not lines[i].strip().startswith("Ответственный:"):
                    # Одна строка до "Ответственный:"
                    output_file.write("Задача: " + lines[i].strip() + "\n")

            elif line.startswith("Срок"):
                output_file.write(line + "\n")
                i += 1
                if i < len(lines) and lines[i].strip().startswith("В части Проекта"):
                    # Возвращаемся к нормальной обработке с "В части Проекта"
                    continue
                elif i < len(lines) and not lines[i].strip().startswith("Ответственный:"):
                    next_line = lines[i].strip()
                    if (i + 1 < len(lines) and
                        not lines[i+1].strip().startswith("Ответственный:")):
                        output_file.write("Подроект: " + next_line + "\n")
                        i += 1
                        output_file.write("Задача: " + lines[i].strip() + "\n")
                    else:
                        output_file.write("Задача: " + next_line + "\n")

            elif line.startswith("Ответственный:"):
                output_file.write(line + "\n")

            else:
                output_file.write(line + "\n")

            i += 1

def separate_messages_for_telegram(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as txt_file:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            for line in txt_file:
                line = line.strip()
                if line.startswith("Задача:"):
                    out_file.write(f"<br>{line}\n")
                    out_file.write("---\n")
                elif line.startswith("Ответственный:"):
                    out_file.write(f"{line}\n")
                    out_file.write("---\n")
                elif line.startswith("Срок:"):
                    out_file.write(f"{line}\n")
                    out_file.write("---\n")
                else: out_file.write(f"{line}\n")






# ######## База данных ########

# @bot.callback_query_handler(func=lambda callback:True)
# def callback_message(callback):
#     if callback.data == 'report_project':
#         markup = types.InlineKeyboardMarkup()
#         button_report_project = types.InlineKeyboardButton('Все проекты',
#                                                            callback_data='all_projects')
#         markup.row(button_report_project)
#         bot.reply_to(callback.message, 'Выберите проект', reply_markup=markup)
#
#
# @bot.message_handler(commands=['show_db'])
# def reading_file(message):
#     tables = ["alembic_version", "roles", "task", "task_assignments", "users"]
#
#     with closing(psycopg2.connect(dbname=DBNAME, user=USER,
#                         password=PASSWORD, host=HOST, port=PORT)) as conn:
#         with conn.cursor() as cursor:
#             for table in tables:
#                 print(f"Содержимое таблицы {table}:")
#                 cursor.execute(f"SELECT * FROM {table}")
#                 for row in cursor:
#                     print(row)
#                 print()
#                 users = cursor.fetchall()
#                 info = ''
#                 for el in users:
#                     info += ""


# def download_tasks_to_db(message):
#     with closing(psycopg2.connect(dbname=DBNAME, user=USER,
#                         password=PASSWORD, host=HOST, port=PORT)) as conn:
#         with conn.cursor() as cursor:
#             cursor.execute("INSERT INTO task (task_creator_id, task_executor_id, task_name, subtack_name, task_description, created_at, deadline, state, comment) VALUES (:task_creator_id, :task_executor)")
#             for row in cursor:
#                 print(row[0])


# ############ frontend ############

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

@bot.callback_query_handler(func=lambda call: call.data == 'view_uploaded_document')
def upload_new_document(call):
    bot.send_message(call.message.chat.id, "Раннее загруженных документов не найдено")
    bot.send_message(call.message.chat.id, "Пожалуйста, загрузите новый документ")

@bot.callback_query_handler(func=lambda call: call.data == 'upload_a_new_document')
def upload_new_document(call):
    bot.send_message(call.message.chat.id, "Пожалуйста, загрузите новый документ")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    global FILE_ID, FILE_INFO, FILE_URL
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

    FILE_ID = message.document.file_id
    FILE_INFO = bot.get_file(FILE_ID)
    FILE_URL = f'https://api.telegram.org/file/bot{TOKEN}/{FILE_INFO.file_path}'

def create_report_projects(message, file_path):
    answer_df = all_text(file_path)
    answer_df = answer_df.dropna()
    answer_df = answer_df.apply(lambda x: x.map(lambda y: re.sub(r'^\s+|\s+$', '', y, flags=re.M)))
    answer_text = answer_df.apply(lambda row: ' '.join(row), axis=1)
    answer_text = answer_text[answer_text != '']

    if answer_text.empty:
        bot.send_message(message.chat.id, "Извините, но этот файл пустой.")
    else:
        for chunk in split_text('\n'.join(answer_text), chunk_size=3000):
            bot.send_message(message.chat.id, chunk)

    os.remove(file_path)


def create_report_projects_2(message, file_path):
    # Convert docx to txt
    document = Document(file_path)
    text = "\n".join([para.text for para in document.paragraphs])

    # Remove text before keyword
    keyword = "РЕШИЛИ:"
    start_index = text.find(keyword)
    if start_index != -1:
        text = text[start_index + len(keyword):]

    # Clean text
    text = re.sub(r'\n{2,}', '\n', text)

    # Add keys to source text
    lines = text.split('\n')
    result_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("В части Проекта"):
            result_lines.append("Проект: " + line)
            i += 1
            if i < len(lines) and lines[i].strip().startswith("Ответственный:"):
                # No additional lines between
                pass
            elif (i + 1 < len(lines) and
                  not lines[i+1].strip().startswith("Ответственный:")):
                # Two lines before "Ответственный:"
                result_lines.append("Подпроект: " + lines[i].strip())
                i += 1
                result_lines.append("Задача: " + lines[i].strip())
            elif i < len(lines) and not lines[i].strip().startswith("Ответственный:"):
                # One line before "Ответственный:"
                result_lines.append("Задача: " + lines[i].strip())

        elif line.startswith("Срок"):
            result_lines.append(line)
            i += 1
            if i < len(lines) and lines[i].strip().startswith("В части Проекта"):
                # Back to normal processing with "В части Проекта"
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

    # Separate messages for Telegram
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
        else:
            telegram_text += f"{line}\n"

    # Send message
    if telegram_text.strip() == "":
        bot.send_message(message.chat.id, "Извините, но этот файл пустой.")
    else:
        for line in telegram_text.split('<br>'):
            bot.send_message(message.chat.id, line)

    os.remove(file_path)

@bot.callback_query_handler(func=lambda call: call.data == 'report_project')
def report_project_callback(call):
    global FILE_ID, FILE_INFO, FILE_URL
    if FILE_ID and FILE_INFO and FILE_URL:
        output_path = './temp/'
        downloaded_file_path = download(FILE_URL, out=output_path)
        # create_report_projects(call.message, downloaded_file_path)
        create_report_projects_2(call.message, downloaded_file_path)
    else:
        bot.send_message(call.message.chat.id, "Ошибка: файл не найден.")


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
