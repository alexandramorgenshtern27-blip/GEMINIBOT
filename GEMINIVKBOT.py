import os
import sys
import subprocess

# Функция для мгновенной печати в логи (чтобы ты видела процесс)
def log(msg):
    print(f"--- {msg} ---", flush=True)

# 1. ПРИНУДИТЕЛЬНАЯ УСТАНОВКА (без импортов в начале!)
def install_requirements():
    log("ПРОВЕРКА БИБЛИОТЕК...")
    # Список того, что нам жизненно необходимо
    packages = ["vkbottle", "google-genai", "python-docx", "requests", "python-dotenv"]
    
    for pkg in packages:
        try:
            # Пытаемся проверить наличие (хитрым способом без import)
            log(f"Проверяю {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "show", pkg.split('==')[0]], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            log(f"Библиотека {pkg} не найдена. Устанавливаю...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", pkg])
            log(f"Успешно установлено: {pkg}")

# Сначала ставим всё
try:
    install_requirements()
except Exception as e:
    log(f"КРИТИЧЕСКАЯ ОШИБКА ПРИ УСТАНОВКЕ: {e}")
    sys.exit(1)

# 2. ТЕПЕРЬ МОЖНО ИМПОРТИРОВАТЬ
log("ВСЕ БИБЛИОТЕКИ НА МЕСТЕ. ИМПОРТИРУЮ...")
import io
import requests
from python_dotenv import load_dotenv
from google import genai
from google.genai import types
from vkbottle import Keyboard, KeyboardButtonColor, Text, Bot, Message
from docx import Document

load_dotenv()

# ================= НАСТРОЙКИ ИЗ ENV =================
VK_TOKEN = os.getenv("VK_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

if not VK_TOKEN or not GEMINI_KEY:
    log("ОШИБКА: Ключи не найдены в переменных окружения хостинга!")
    sys.exit(1)

# Инициализация
client = genai.Client(api_key=GEMINI_KEY)
bot = Bot(token=VK_TOKEN)

@bot.on.message()
async def handle(message: Message):
    if not message.text: return
    log(f"Новое сообщение: {message.text[:15]}...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[message.text],
            config=types.GenerateContentConfig(system_instruction="ты дерзкий гений")
        )
        await message.answer(response.text)
        log("Ответил успешно")
    except Exception as e:
        log(f"Ошибка Gemini: {e}")
        await message.answer(f"мозг поплыл: {e}")

if __name__ == "__main__":
    log("БОТ ПОДКЛЮЧАЕТСЯ К ВК...")
    bot.run_forever()
