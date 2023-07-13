import telebot
from telebot import types
import os
import subprocess
import time
from config import api_bot

bot = telebot.TeleBot(api_bot)

bot_is_busy = False
waiting_users = []
authorized_users = [576891495, 374489044, 6104519444]
markup_cache = None

def generate_markup():
    global markup_cache
    if markup_cache is None:
        keyboard = types.InlineKeyboardMarkup()
        button_run_script = types.InlineKeyboardButton(text="Запустить Rpyrogram.py", callback_data='run_script')
        keyboard.add(button_run_script)
        markup_cache = keyboard
    return markup_cache

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in authorized_users:
        bot.send_message(message.chat.id, 'Извините, вы не авторизованы для использования этого бота.')
        return
    markup = generate_markup()
    bot.send_message(message.chat.id, 'Пожалуйста, выберите:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global bot_is_busy, waiting_users

    if call.message.chat.id not in authorized_users:
        bot.answer_callback_query(call.id, 'Извините, вы не авторизованы для использования этого бота.')
        return

    if call.data == 'run_script':
        if bot_is_busy:
            bot.answer_callback_query(call.id, "Бот сейчас занят, попробуйте позже")
            if call.message.chat.id not in waiting_users:
                waiting_users.append(call.message.chat.id)
            return

        bot_is_busy = True

        try:
            process = subprocess.Popen(['python3', 'Rpyrogram.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            dots = "."
            message = bot.send_message(call.message.chat.id, f"Скрипт начал работу{dots}")
            while process.poll() is None:
                dots = "." if len(dots) > 2 else dots + "."
                message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=message.message_id, text=f"Скрипт начал работу{dots}")
                time.sleep(1)

            if process.returncode != 0:
                bot.send_message(call.message.chat.id, "ОШИБКА! НЕОБХОДИМО ВМЕШАТЕЛЬСТВО СПЕЦИАЛИСТА. ОШИБКА! \nПроблема с парсингом")
            else:
                if os.path.isfile('telegram_messages_0.docx'):
                    with open('telegram_messages_0.docx', 'rb') as doc:
                        bot.send_document(call.message.chat.id, doc)

                    bot.send_message(call.message.chat.id, "Скрипт успешно завершил работу, файл прикреплен")
                else:
                    bot.send_message(call.message.chat.id, "Скрипт завершил работу, но файл не найден")

            bot.send_message(call.message.chat.id, "Бот снова свободен. Работаем дальше?", reply_markup=generate_markup())

            for user in waiting_users:
                bot.send_message(user, "Бот теперь свободен, вы можете начать новую задачу.")
            waiting_users = []

        except Exception as e:
            bot.send_message(call.message.chat.id, "ОШИБКА! НЕОБХОДИМО ВМЕШАТЕЛЬСТВО СПЕЦИАЛИСТА. ОШИБКА! \n Проблема с ботом", reply_markup=generate_markup())
            print(e)
        finally:
            bot_is_busy = False

bot.polling()
