import os
import sys
import time

def log(msg):
    print(f">>> [DEBUG]: {msg}", flush=True)

log("1. Скрипт запущен. Жду 5 секунд, чтобы стабилизировать RAM...")
time.sleep(5)

try:
    log("2. Пробую импортировать google-genai...")
    from google import genai
    from google.genai import types
    log("   - OK: google-genai загружен.")
    
    log("3. Жду 3 секунды перед vkbottle...")
    time.sleep(3)
    
    log("4. Пробую импортировать vkbottle...")
    from vkbottle.bot import Bot, Message
    log("   - OK: vkbottle загружен.")

except Exception as e:
    log(f"!!! ОШИБКА ПРИ ИМПОРТЕ: {e}")
    sys.exit(1)

log("5. Все либы на месте. Проверяю ключи...")
VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not VK_TOKEN or not GEMINI_KEY:
    log("!!! ОШИБКА: Ключи не найдены в Env Variables!")
    sys.exit(1)

log("6. Инициализация клиентов...")
try:
    client = genai.Client(api_key=GEMINI_KEY)
    bot = Bot(token=VK_TOKEN)
    log("7. Клиенты созданы. Погнали!")
except Exception as e:
    log(f"!!! ОШИБКА КЛИЕНТОВ: {e}")
    sys.exit(1)

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
        log(f"Ошибка в чате: {e}")

if __name__ == "__main__":
    bot.run_forever()
