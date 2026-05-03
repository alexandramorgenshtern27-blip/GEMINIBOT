import os
import io
import sys
import requests
from python_dotenv import load_dotenv

# Принудительный вывод логов
def log(msg):
    print(f"--- {msg} ---", flush=True)

log("ЗАПУСК СКРИПТА")
load_dotenv()

try:
    from google import genai
    from google.genai import types
    from vkbottle import Keyboard, KeyboardButtonColor, Text, DocMessagesUploader, PhotoMessageUploader
    from vkbottle.bot import Bot, Message
    from docx import Document
    log("ВСЕ БИБЛИОТЕКИ ИМПОРТИРОВАНЫ")
except ImportError as e:
    log(f"ОШИБКА ИМПОРТА: {e}")
    log("Скорее всего, хостинг не установил библиотеки из requirements.txt")
    sys.exit(1)

# Данные
VK_TOKEN = os.getenv("VK_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

if not VK_TOKEN or not GEMINI_KEY:
    log("КРИТИЧЕСКАЯ ОШИБКА: КЛЮЧИ НЕ НАЙДЕНЫ В ENV")
    sys.exit(1)

try:
    client = genai.Client(api_key=GEMINI_KEY)
    bot = Bot(token=VK_TOKEN)
    log("API КЛИЕНТЫ ИНИЦИАЛИЗИРОВАНЫ")
except Exception as e:
    log(f"ОШИБКА ИНИЦИАЛИЗАЦИИ: {e}")
    sys.exit(1)

@bot.on.message()
async def handler(message: Message):
    if not message.text: return
    log(f"ПОЛУЧЕНО СООБЩЕНИЕ: {message.text[:20]}...")
    
    await message.answer("погоди рожаю ответ...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[message.text],
            config=types.GenerateContentConfig(
                system_instruction="ты хамоватый гений"
            )
        )
        await message.answer(response.text)
        log("ОТВЕТ ОТПРАВЛЕН")
    except Exception as e:
        log(f"ОШИБКА ГЕНЕРАЦИИ: {e}")
        await message.answer(f"мозг поплыл: {e}")

if __name__ == "__main__":
    log("БОТ ПОДКЛЮЧАЕТСЯ К ВК (LONGPOLL)...")
    try:
        bot.run_forever()
    except Exception as e:
        log(f"БОТ УПАЛ ПРИ РАБОТЕ: {e}")
