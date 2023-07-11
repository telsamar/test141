from pyrogram import Client, filters
from config import api_id, api_hash

app = Client("my_account", api_id=api_id, api_hash=api_hash)

with open('dictionary.txt') as f:
    words = [word.strip().lower() for word in f.readlines()]

with open('channels.txt', 'r') as f:
    channels = [line.strip().lower() for line in f]

@app.on_message(filters.channel)
async def handle_channel_update(client, message):
    nomer = 1
    if message.chat.username in channels:
        if (message.text and any(word in message.text.lower() for word in words)) or (message.caption and any(word in message.caption.lower() for word in words)):
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            post_link = f"https://t.me/{message.chat.username}/{message.id}"
            print(f'Nomer: {nomer}')
            print(f"Новое сообщение в канале: {message.chat.title}")
            print(f"Текст сообщения: {message.text}")
            print(f'Caption: {message.caption}')
            print(f'Link: {post_link}')
            if message.photo:
                print("Есть фото")
            else:
                print("Нет фото")

            if message.video:
                print("Есть видео")
            else:
                print("Нет видео")
            if message.document:
                print("Есть прикрепленный документ")
            else:
                print("Нет прикрепленного документа")

            nomer += 1

print("Программа запущена. Ожидание новых сообщений...")
app.run()