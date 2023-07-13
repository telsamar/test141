import telebot
from telebot import types
import os
import subprocess
from config import api_bot

bot = telebot.TeleBot(api_bot)

# Флаг, показывающий занятость бота
bot_is_busy = False

# Список пользователей, которые попытались запустить бота, когда он был занят
waiting_users = []

def generate_markup():
    keyboard = types.InlineKeyboardMarkup()
    button_run_script = types.InlineKeyboardButton(text="Запустить Rpyrogram.py", callback_data='run_script')
    keyboard.add(button_run_script)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = generate_markup()
    bot.send_message(message.chat.id, 'Пожалуйста, выберите:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global bot_is_busy, waiting_users

    if call.data == 'run_script':
        if bot_is_busy:
            bot.answer_callback_query(call.id, "Бот сейчас занят, попробуйте позже")
            if call.message.chat.id not in waiting_users:
                waiting_users.append(call.message.chat.id)
            return

        bot_is_busy = True

        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Скрипт начал работу")

            # subprocess.run() ожидает завершения вызываемого процесса
            subprocess.run(['python3', 'Rpyrogram.py'], check=True)

            # Проверяем, существует ли файл
            if os.path.isfile('telegram_messages_0.docx'):
                with open('telegram_messages_0.docx', 'rb') as doc:
                    bot.send_document(call.message.chat.id, doc)

                bot.send_message(call.message.chat.id, "Скрипт успешно завершил работу, файл прикреплен")
            else:
                bot.send_message(call.message.chat.id, "Скрипт завершил работу, но файл не найден")

            bot.send_message(call.message.chat.id, "Бот снова свободен. Работаем дальше?", reply_markup=generate_markup())

            for user in waiting_users:
                bot.send_message(user, "Бот теперь свободен, вы можете начать новую задачу.", reply_markup=generate_markup())
            waiting_users = []

        except Exception as e:
            bot.send_message(call.message.chat.id, f"Произошла ошибка при запуске скрипта: {str(e)}")

        finally:
            bot_is_busy = False

bot.polling()
