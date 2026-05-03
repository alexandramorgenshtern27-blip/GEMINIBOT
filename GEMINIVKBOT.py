import os
import sys
from vkbottle import Bot, Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Message # Вот это критически важно для vkbottle 4.8+
from google import genai
from google.genai import types

def log(msg):
    print(f"--- {msg} ---", flush=True)

# Проверка ключей сразу при старте
VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not VK_TOKEN or not GEMINI_KEY:
    log("КРИТИЧЕСКАЯ ОШИБКА: Ключи не найдены в Environment Variables!")
    sys.exit(1)

bot = Bot(token=VK_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

@bot.on.message()
async def handler(message: Message):
    if not message.text: return
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[message.text]
        )
        await message.answer(response.text)
    except Exception as e:
        log(f"Ошибка Gemini: {e}")

if __name__ == "__main__":
    log("БОТ ЗАПУСКАЕТСЯ...")
    bot.run_forever()
