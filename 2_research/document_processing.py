from libraries import *

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