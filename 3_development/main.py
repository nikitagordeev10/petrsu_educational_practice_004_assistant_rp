from libraries import *
from password import *
TOKEN = open('token.txt', 'r').read()
bot = telebot.TeleBot(TOKEN)

# ############ backend ############

def process_document(message, file_path):
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

    system('rm -vf ' + file_path)

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
    """Функция для обработки текста и извлечения задач, ответственных лиц и дат."""
    tasks = []  # Список для хранения задач
    responsible = ""  # Переменная для хранения ответственного лица
    deadline = ""  # Переменная для хранения даты
    start_processing = False  # Флаг для указания начала обработки

    # Разбиваем текст на строки и проходим по каждой строке
    for line in text.split('\n'):
        if start_processing:  # Если начали обработку
            if line.strip():  # Если строка не пустая
                # Проверяем, соответствует ли строка формату "Ответственный: ..."
                match_responsible = re.match(r'^Ответственный: (.+)', line)
                # Проверяем, соответствует ли строка формату "Срок: ..."
                match_date = re.match(r'^\s*Срок: (.+)', line)
                if match_responsible:  # Если строка соответствует формату "Ответственный: ..."
                    responsible = match_responsible.group(1)  # Запоминаем ответственного
                elif match_date:  # Если строка соответствует формату "Срок: ..."
                    deadline = match_date.group(1)  # Запоминаем дату
                else:
                    tasks.append([line.strip(), responsible, deadline])  # Добавляем задачу в список
        elif line.startswith('В части Проекта'):  # Если строка начинается с "В части Проекта"
            start_processing = True  # Устанавливаем флаг начала обработки

    # Создаем DataFrame из списка задач
    return pd.DataFrame(tasks, columns=['Задача', 'Ответственный', 'Дата'])

def get_docx_data(path):
    """Функция для извлечения данных из документа формата .docx и преобразования их в табличный вид."""
    doc = docx.Document(path)  # Открываем документ .docx
    full_text = ""  # Переменная для хранения полного текста документа
    tables = []  # Список для хранения таблиц
    found = False  # Флаг для указания нахождения начала обработки

    # Проходим по каждому абзацу документа
    for paragraph in doc.paragraphs:
        if found:  # Если начали обработку
            if paragraph.text.startswith('В части Проекта'):  # Если абзац начинается с "В части Проекта"
                tables.append(process_text(full_text))  # Обрабатываем текст и добавляем таблицу в список
                full_text = ""  # Очищаем переменную для хранения текста
            full_text += paragraph.text + '\n'  # Добавляем текст абзаца к полному тексту
        elif re.match(r'^\s*РЕШИЛИ:', paragraph.text):  # Если абзац начинается с "РЕШИЛИ:"
            found = True  # Устанавливаем флаг начала обработки
            full_text += paragraph.text + '\n'  # Добавляем текст абзаца к полному тексту

    # Добавляем последнюю таблицу
    tables.append(process_text(full_text))

    # Объединяем все таблицы в одну и возвращаем её
    return pd.concat(tables, ignore_index=True)




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

def new_convert_file():
    convert_docx_to_txt(r"Протокол совещания_24.04.11.docx", 'status_1.txt')
    save_text_after_keyword("status_1.txt", "РЕШИЛИ:", "status_2.txt")
    clean_text('status_2.txt', 'status_3.txt')
    adding_keys_to_source_text('status_3.txt', 'status_4.txt')
    separate_messages_for_telegram ('status_4.txt', 'status_5.txt')

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