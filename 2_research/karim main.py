import telebot
from telebot import types
bot = telebot.TeleBot('7128913627:AAESNGo1asXy2y6XHQRg-M73j6LrZLBrgSI')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('Загрузить файл')
    markup.add(button)
    bot.send_message(message.chat.id, "Загрузите файл", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Загрузить файл':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Сформировать отчет по проектам')
        button2 = types.KeyboardButton('Сформировать отчет по практике по ответственным')
        button3 = types.KeyboardButton('Сформировать отчет по срокам')
        button4 = types.KeyboardButton('Добавить задачу')
        markup.add(button1, button2, button3, button4)
        bot.send_message(message.chat.id, 'Выберите одну из следующих опций:', reply_markup=markup)
    elif message.text == 'Сформировать отчет по проектам':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Все проекты')
        button2 = types.KeyboardButton('Коммод')
        button3 = types.KeyboardButton('АСУ ЭТО и АСУ ТМО')
        button4 = types.KeyboardButton('ТПИР')
        markup.add(button1, button2, button3, button4)
        bot.send_message(message.chat.id, 'Выберите одну из следующих опций:', reply_markup=markup)
    elif message.text == 'Коммод':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton('Изменить информацию')
        markup.add(button)
        bot.send_message(message.chat.id, 'Выберите одну из следующих опций:', reply_markup=markup)
    elif message.text == 'Изменить информацию':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Задача')
        button2 = types.KeyboardButton('Ответсвенный')
        button3 = types.KeyboardButton('Срок')
        button4 = types.KeyboardButton('Статус')
        button5 = types.KeyboardButton('Комментарии')
        markup.add(button1, button2, button3, button4, button5)
        bot.send_message(message.chat.id, 'Какую информацию вы хотите изменить?', reply_markup=markup)




bot.polling(none_stop=True)