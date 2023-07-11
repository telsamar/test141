import asyncio
from pyrogram import Client, filters
from datetime import datetime, timezone
from docx import Document
from docx.shared import Inches
from docx.shared import Pt
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from config import api_id, api_hash


with open('dictionary.txt') as f:
    words = [word.strip().lower() for word in f.readlines()]

with open('channels.txt') as f:
    channels = [channel.strip() for channel in f.readlines()]

filename = 'telegram_messages.docx'
screenshot_path = "screen"

chrome_options = Options()
chrome_options.add_argument("--headless")

webdriver_service = Service(ChromeDriverManager().install())

try:
    doc = Document(filename)
except:
    doc = Document()

async def main():
    app = Client("my_account2", api_id=api_id, api_hash=api_hash)
    await app.start()
    print("Bot started...")
    time_limit = 2
    nomer = 1
    for channel_name in channels:
        async for message in app.get_chat_history(channel_name):
            time_difference = datetime.now(timezone.utc) - message.date.astimezone(timezone.utc)
            time_difference_seconds = time_difference.total_seconds()
            if time_difference_seconds < time_limit*3600:
                post_link = f"https://t.me/{channel_name}/{message.id}"  
    
                if ((message.text is not None and message.text.strip() != "" and any(word in message.text.lower() for word in words)) or 
                    (message.caption is not None and message.caption.strip() != "" and any(word in message.caption.lower() for word in words))):

                    table = doc.add_table(rows=1, cols=2)
                    for i, name in enumerate(["Номер", "Ссылка"]):
                        cell = table.cell(0, i)
                        cell.text = name
                    table.columns[0].width = Inches(1.0/3)
                    border_str = '<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:top w:val="single"/><w:left w:val="single"/><w:bottom w:val="single"/><w:right w:val="single"/></w:tcBorders>'
                    for cell in table.rows[0].cells:
                        border_elm = parse_xml(border_str)
                        cell._element.get_or_add_tcPr().append(border_elm)

                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    # print(message)
                    doc.add_paragraph(f'Nomer: {nomer}')
                    doc.add_paragraph(f'Text: {message.text}')
                    doc.add_paragraph(f'Caption: {message.caption}')
                    doc.add_paragraph(f'Link: {post_link}')

                    cells = table.add_row().cells
                    cells[0].text = str(nomer)
                    cells[1].text = post_link
                    for cell in cells:
                        border_elm = parse_xml(border_str)
                        cell._element.get_or_add_tcPr().append(border_elm)
                    

                    print(f'Link: {post_link}')
                    print(f'Caption: {message.caption}')
                    print(f'Text: {message.text}')

                    if message.photo:
                        print("Есть фото")
                        doc.add_paragraph('Есть фото')
                    else:
                        print("Нет фото")
                        doc.add_paragraph('Нет фото!!!!!!!!!!!!!!')

                    if message.video:
                        print("Есть видео")
                        doc.add_paragraph('Есть видео')
                    else:
                        print("Нет видео")
                        doc.add_paragraph('Нет видео!!!!!!!!!!!!!!')

                    if message.document:
                        print("Есть прикрепленный документ")
                        doc.add_paragraph('Есть прикрепленный документ')
                    else:
                        print("Нет прикрепленного документа")
                        doc.add_paragraph('Нет прикрепленного документа!!!!!!!!!!!!!!')

                    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
                    driver.get(post_link)
                    driver.set_window_size(1500, 3000)

                    element = driver.find_element(By.CLASS_NAME, "tgme_page_widget")
                    ActionChains(driver).move_to_element(element).perform()

                    screenshot_filename = screenshot_path + f'/screenshot_{nomer}.png'
                    element.screenshot(screenshot_filename)
                    driver.quit()
                    doc.add_picture(screenshot_filename, width=Inches(5))
                    doc.save(filename)
                    os.remove(screenshot_filename)
                    
                    nomer += 1
            else:
                break
    print("Ожидание завершения - 3 секунды")
    await asyncio.sleep(3)
    await app.stop()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(main())
finally:
    pending = asyncio.all_tasks(loop=loop)
    for task in pending:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    loop.close()