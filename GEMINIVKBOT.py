import os
import sys
import subprocess

def log(msg):
    print(f"--- {msg} ---", flush=True)

# 1. Установка без лишних слов
def install_requirements():
    log("ЖЕСТКАЯ УСТАНОВКА ПАКЕТОВ")
    # Убираем dotenv, ставим только базу
    packages = ["vkbottle", "google-genai", "python-docx", "requests"]
    
    for pkg in packages:
        log(f"Ставлю/обновляю {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", pkg])
    
    # Магия: принудительно обновляем пути, чтобы Python увидел новые папки
    import site
    from importlib import reload
    reload(site)

install_requirements()

# 2. ИМПОРТЫ (БЕЗ DOTENV)
log("ИМПОРТИРУЮ ОСНОВНОЙ КОД")
import io
import requests
from google import genai
from google.genai import types
from vkbottle import Keyboard, KeyboardButtonColor, Text, Bot, Message

# БЕРЕМ НАПРЯМУЮ ИЗ СИСТЕМЫ (из тех полей, что ты заполняла на сайте)
VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not VK_TOKEN or not GEMINI_KEY:
    log("КРИТИЧЕСКАЯ ОШИБКА: Ключи не найдены в переменных окружения хостинга!")
    log("Зайди в панель хостинга и добавь VK_TOKEN и GEMINI_KEY")
    sys.exit(1)

log(f"Токен ВК найден (начинается на {VK_TOKEN[:5]}...)")

try:
    client = genai.Client(api_key=GEMINI_KEY)
    bot = Bot(token=VK_TOKEN)
    log("БОТ ГОТОВ К РАБОТЕ")
except Exception as e:
    log(f"ОШИБКА НА СТАРТЕ: {e}")
    sys.exit(1)

@bot.on.message()
async def handle(message: Message):
    if not message.text: return
    log(f"Сообщение: {message.text[:15]}")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Версия 2.0 или 1.5, проверь свою
            contents=[message.text],
            config=types.GenerateContentConfig(system_instruction="ты хамоватый гений")
        )
        await message.answer(response.text)
        log("Ответил")
    except Exception as e:
        log(f"Ошибка Gemini: {e}")
        await message.answer(f"мозг поплыл: {e}")

if __name__ == "__main__":
    log("ЗАПУСКАЮ LONGPOLL...")
    bot.run_forever()
