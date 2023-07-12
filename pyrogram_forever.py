import re
import logging
import sys
from pyrogram import Client, filters
from config import api_id, api_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

message_count = 0

app = Client("my_account", api_id=api_id, api_hash=api_hash)

def read_patterns(file_name):
    with open(file_name) as f:
        return [re.compile(pattern.strip()) for pattern in f.readlines()]

def read_channels(file_name):
    with open(file_name, 'r') as f:
        return [line.strip().lower() for line in f.readlines()]

try:
    patterns = read_patterns('regex_patterns.txt')
    channels = read_channels('channels.txt')
except Exception as e:
    logger.error(f'Error reading files: {str(e)}')
    sys.exit(1)

@app.on_message(filters.channel)
async def handle_channel_update(client, message):
    global message_count
    if message.chat.username in channels:
        if (message.text and any(pattern.search(message.text) for pattern in patterns)) or (message.caption and any(pattern.search(message.caption) for pattern in patterns)):
            logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            post_link = f"https://t.me/{message.chat.username}/{message.id}"
            message_count += 1
            logger.info(f'Nomer: {message_count}')
            logger.info(f"Новое сообщение в канале: {message.chat.title}")
            logger.info(f"Текст сообщения: {message.text}")
            logger.info(f'Caption: {message.caption}')
            logger.info(f'Link: {post_link}')
            if message.photo:
                logger.info("Есть фото")
            else:
                logger.info("Нет фото")

            if message.video:
                logger.info("Есть видео")
            else:
                logger.info("Нет видео")
            if message.document:
                logger.info("Есть прикрепленный документ")
            else:
                logger.info("Нет прикрепленного документа")

logger.info("Программа запущена. Ожидание новых сообщений...")
app.run()
