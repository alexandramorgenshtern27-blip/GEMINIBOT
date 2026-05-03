print("--- ИНИЦИАЛИЗАЦИЯ ЗАПУЩЕНА ---", flush=True)
import os
import subprocess
import sys

# 1. ГРУБАЯ УСТАНОВКА (сначала ставим, потом импортируем)
def bootstrap():
    required = ["vkbottle", "google-genai", "python-docx", "requests", "python-dotenv"]
    print("--- ПРОВЕРКА ОКРУЖЕНИЯ ---")
    for pkg in required:
        try:
            # Пытаемся понять, установлен ли пакет
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"--- Устанавливаю {pkg}... ---")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Запускаем установку до всех импортов
bootstrap()

# 2. ТЕПЕРЬ ИМПОРТЫ (когда всё точно стоит)
import io
import requests
from python_dotenv import load_dotenv
from google import genai
from google.genai import types
from vkbottle import Keyboard, KeyboardButtonColor, Text, DocMessagesUploader, PhotoMessageUploader
from vkbottle.bot import Bot, Message
from docx import Document
from typing import Dict

# Загружаем ключи
load_dotenv()

# ================= НАСТРОЙКИ =================
VK_TOKEN = os.getenv("VK_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Проверка ключей
if not VK_TOKEN or not GEMINI_KEY:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Ключи не заданы в переменных окружения хостинга!")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_KEY)
MODEL_NAME = "gemini-2.5-flash" 

bot = Bot(token=VK_TOKEN)
photo_uploader = PhotoMessageUploader(bot.api)
doc_uploader = DocMessagesUploader(bot.api)

sessions: Dict[int, dict] = {}

SYSTEM_PROMPT = (
    "ты гений с мировым именем но при этом дерзкий и хамоватый тип "
    "на научные темы отвечай академично и сложно как профессор "
    "в бытовом общении пиши только с маленькой буквы без запятых юзай сленг типа крутой челик на чилле "
    "импровизируй в хамстве не повторяйся"
)

def get_format_keyboard():
    kb = Keyboard(one_time=True, inline=False)
    kb.add(Text("скинь текстом"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("сделай файл"), color=KeyboardButtonColor.POSITIVE)
    return kb.get_json()

@bot.on.message()
async def main_handler(message: Message):
    uid = message.from_id
    text = message.text or ""
    
    if text.lower() in ["скинь текстом", "сделай файл"]:
        # (Тут логика отправки файла/текста из предыдущих версий, 
        # для краткости пропустим, но она будет работать если добавить)
        return

    prompt_parts = [text] if text else []
    
    if message.attachments:
        await message.answer("вижу твой хлам ща чекну...")
        for att in message.attachments:
            if att.photo:
                img_data = requests.get(att.photo.sizes[-1].url).content
                prompt_parts.append(types.Part.from_bytes(data=img_data, mime_type="image/jpeg"))

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_parts,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        )
        ans_text = response.text
        sessions[uid] = {"last_res": ans_text}
        await message.answer(ans_text, keyboard=get_format_keyboard())
    except Exception as e:
        await message.answer(f"мозг поплыл: {e}")

if __name__ == "__main__":
    print("--- БОТ В СЕТИ ---")
    bot.run_forever()
