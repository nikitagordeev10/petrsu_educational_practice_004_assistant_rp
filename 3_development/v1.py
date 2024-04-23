from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import docx

# Функция для анализа протокола совещания
def analyze_protocol(file_path):
    doc = docx.Document(file_path)
    tasks = []

    for paragraph in doc.paragraphs:
        if paragraph.text.startswith("РЕШИЛИ:"):
            for item in paragraph._element.getnext().getchildren():
                task = {}
                if item.tag.endswith("}t"):
                    task["description"] = item.text.strip()
                elif item.tag.endswith("}r"):
                    for subitem in item.getchildren():
                        if subitem.tag.endswith("}t"):
                            text = subitem.text.strip()
                            if text.startswith("Ответственный:"):
                                task["responsible"] = text.split(":")[1].strip()
                            elif text.startswith("Срок:"):
                                task["deadline"] = text.split(":")[1].strip()
                    tasks.append(task)

    return tasks

# Функция для формирования майнд карты
def create_mind_map(tasks):
    mind_map = "Название проекта\tДата\tЗадача\tОтветственный\n"
    for task in tasks:
        mind_map += f"Проект\t{task.get('deadline', '')}\t{task.get('description', '')}\t{task.get('responsible', '')}\n"
    return mind_map

# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Пожалуйста, отправьте протокол совещания в формате .docx.')

# Обработчик текстовых сообщений
def analyze_document(update: Update, context: CallbackContext) -> None:
    file_id = update.message.document.file_id
    file = context.bot.get_file(file_id)
    file_path = f"downloads/{file.file_path}"
    file.download(file_path)

    tasks = analyze_protocol(file_path)
    mind_map = create_mind_map(tasks)

    update.message.reply_text(mind_map)

def main() -> None:
    # Инициализация бота
    updater = Updater("TOKEN")
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))

    # Обработчик присланных документов
    dispatcher.add_handler(MessageHandler(Filters.document, analyze_document))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
