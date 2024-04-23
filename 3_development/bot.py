from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from docx import Document
import re

# Функция для обработки документа
def process_docx(file_path):
    doc = Document(file_path)
    tasks = []

    for para in doc.paragraphs:
        text = para.text
        if "РЕШИЛИ:" in text:
            project_name = text.split(':')[1].strip()
        # Примерный regex для извлечения данных
        m = re.match(r'\d+\.\s(.+?Ответственный:\s.+\sСрок:\s.+\)', text)
        if m:
            tasks.append((project_name, m.group(1)))

    return tasks

# Функция для обработки сообщений
def docx_handler(update: Update, context: CallbackContext) -> None:
    document = context.bot.get_file(update.message.document.file_id)
    file_path = 'temp.docx'
    document.download(custom_path = file_path)
    tasks = process_docx(file_path)
    response = "Задачи:\n"
    for project, task in tasks:
        response += f"Проект: {project}\nЗадача: {task}\n"
    update.message.reply_text(response)

def main():
    # Создание Updater и передача токена вашего бота.
    updater = Updater("YOUR_TOKEN_HERE")

    # Получение диспетчера для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик для загружаемых файлов docx
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/vnd.openxmlformats-officedocument.wordprocessingml.document"), docx_handler))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
