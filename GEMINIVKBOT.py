import os
import io
import sys
import requests
from google import genai
from google.genai import types
# ИСПРАВЛЕННЫЙ ИМПОРТ ДЛЯ ТВОЕЙ ВЕРСИИ VKBOTTLE:
from vkbottle import Keyboard, KeyboardButtonColor, Text, Bot
from vkbottle.bot import Message 

# Принудительный вывод логов в консоль
def log(msg):
    print(f"--- {msg} ---", flush=True)

log("ЗАПУСК БОТА...")

# Берем ключи напрямую из системы
VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not VK_TOKEN or not GEMINI_KEY:
    log("ОШИБКА: Ключи не найдены в переменных окружения хостинга!")
    sys.exit(1)

try:
    client = genai.Client(api_key=GEMINI_KEY)
    bot = Bot(token=VK_TOKEN)
    log("ПОДКЛЮЧЕНИЕ УСПЕШНО")
except Exception as e:
    log(f"ОШИБКА ПРИ СТАРТЕ: {e}")
    sys.exit(1)

@bot.on.message()
async def handle_message(message: Message):
    if not message.text:
        return
    
    log(f"Сообщение: {message.text[:20]}...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[message.text],
            config=types.GenerateContentConfig(
                system_instruction="ты хамоватый гений, отвечай дерзко и без заглавных букв"
            )
        )
        await message.answer(response.text)
        log("Ответ отправлен")
    except Exception as e:
        log(f"Ошибка Gemini: {e}")
        await message.answer(f"че-то пошло не так: {e}")

if __name__ == "__main__":
    log("БОТ ВЫШЕЛ В СЕТЬ (LONGPOLL ЗАПУЩЕН)")
    bot.run_forever()
