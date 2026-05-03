import os
import sys

# Маячок №1: Скрипт вообще запустился
print(">>> 1. СКРИПТ СТАРТОВАЛ", flush=True)

try:
    from vkbottle.bot import Bot, Message
    from google import genai
    print(">>> 2. БИБЛИОТЕКИ ИМПОРТИРОВАНЫ", flush=True)
except Exception as e:
    print(f">>> ОШИБКА ИМПОРТА: {e}", flush=True)
    sys.exit(1)

# Маячок №3: Проверка ключей
VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not VK_TOKEN or not GEMINI_KEY:
    print(">>> 3. ОШИБКА: КЛЮЧИ НЕ НАЙДЕНЫ В ПАНЕЛИ ХОСТИНГА", flush=True)
    sys.exit(1)
print(">>> 3. КЛЮЧИ ПОЛУЧЕНЫ", flush=True)

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
        print(f">>> ОТВЕТ ОТПРАВЛЕН ДЛЯ: {message.peer_id}", flush=True)
    except Exception as e:
        print(f">>> ОШИБКА GEMINI: {e}", flush=True)

if __name__ == "__main__":
    print(">>> 4. ЗАПУСКАЮ LONGPOLL (БОТ В СЕТИ)", flush=True)
    bot.run_forever()
