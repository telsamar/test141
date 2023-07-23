import os
import subprocess
import time
import telebot
from telebot import types
from config import api_bot, authorized_users

bot = telebot.TeleBot(api_bot)

bot_is_busy = False
waiting_users = []
markup_cache = None


def generate_markup(stage=None):
    keyboard = types.InlineKeyboardMarkup()

    if stage == 'run_script':
        button_3 = types.InlineKeyboardButton(text="3", callback_data='3')
        button_6 = types.InlineKeyboardButton(text="6", callback_data='6')
        button_12 = types.InlineKeyboardButton(text="12", callback_data='12')
        button_24 = types.InlineKeyboardButton(text="24", callback_data='24')
        keyboard.add(button_3, button_6, button_12, button_24)
    else:
        button_run_script = types.InlineKeyboardButton(
            text="Запустить Rpyrogram.py", callback_data='run_script')
        keyboard.add(button_run_script)

    return keyboard


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in authorized_users:
        bot.send_message(
            message.chat.id, 'Извините, вы не авторизованы для использования этого бота.')
        return
    markup = generate_markup()
    bot.send_message(message.chat.id, 'Пожалуйста, выберите:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global bot_is_busy, waiting_users
    if call.message.chat.id not in authorized_users:
        bot.answer_callback_query(
            call.id, 'Извините, вы не авторизованы для использования этого бота.')
        return

    if bot_is_busy:
        bot.answer_callback_query(call.id, "Бот сейчас занят, попробуйте позже")
        if call.message.chat.id not in waiting_users:
            waiting_users.append(call.message.chat.id)
        return

    if call.data == 'run_script':
        markup = generate_markup(stage='run_script')
        bot.send_message(call.message.chat.id, 'Пожалуйста, выберите:', reply_markup=markup)
    elif call.data in ['3', '6', '12', '24']:
        bot_is_busy = True

        try:
            process = subprocess.Popen(['python3', 'Rpyrogram.py', call.data], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            dots = "."
            message = bot.send_message(
                call.message.chat.id, f"Скрипт начал работу{dots}")
            while process.poll() is None:
                dots = "." if len(dots) > 2 else dots + "."
                message = bot.edit_message_text(chat_id=call.message.chat.id, 
                                                message_id=message.message_id, 
                                                text=f"Скрипт начал работу{dots}")
                time.sleep(1)

            if process.returncode != 0:
                bot.send_message(call.message.chat.id,
                                 "ОШИБКА! НЕОБХОДИМО ВМЕШАТЕЛЬСТВО СПЕЦИАЛИСТА. ОШИБКА! \nПроблема с парсингом")
            else:
                if os.path.isfile('telegram_messages_0.docx'):
                    with open('telegram_messages_0.docx', 'rb') as doc:
                        bot.send_document(call.message.chat.id, doc)

                    bot.send_message(call.message.chat.id,
                                     "Скрипт успешно завершил работу, файл прикреплен")
                else:
                    bot.send_message(
                        call.message.chat.id, "Скрипт завершил работу, но файл не найден")

            markup = generate_markup()
            bot.send_message(
                call.message.chat.id, "Бот снова свободен. Работаем дальше?", reply_markup=markup)

            for user in waiting_users:
                bot.send_message(
                    user, "Бот теперь свободен, вы можете начать новую задачу.", reply_markup=markup)
            waiting_users = []

        except Exception as e:
            bot.send_message(call.message.chat.id,
                             "ОШИБКА! НЕОБХОДИМО ВМЕШАТЕЛЬСТВО СПЕЦИАЛИСТА. ОШИБКА! \n Проблема с ботом", reply_markup=generate_markup())
            print(e)
        finally:
            bot_is_busy = False


bot.infinity_polling()
