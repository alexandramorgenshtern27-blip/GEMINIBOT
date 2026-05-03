import os
import sys
import traceback
import time

# Функция, которая заставляет логи появляться в панели хостинга МОМЕНТАЛЬНО
def log(msg):
    print(f">>> [LOG]: {msg}", flush=True)

log("Инициализация системы логирования...")

try:
    log("Начинаю импорт тяжелых библиотек (vkbottle, google-genai)...")
    from vkbottle.bot import Bot, Message
    from google import genai
    from google.genai import types
    log("Импорт завершен успешно.")

    # Проверка переменных
    VK_TOKEN = os.environ.get("VK_TOKEN")
    GEMINI_KEY = os.environ.get("GEMINI_KEY")

    if not VK_TOKEN or not GEMINI_KEY:
        log("КРИТИЧЕСКАЯ ОШИБКА: Ключи не найдены в Environment Variables!")
        log(f"Доступные переменные: {list(os.environ.keys())}")
        sys.exit(1)

    log("Ключи найдены. Создаю клиентов...")
    bot = Bot(token=VK_TOKEN)
    client = genai.Client(api_key=GEMINI_KEY)
    log("Клиенты созданы. Попытка выхода в сеть...")

    @bot.on.message()
    async def handler(message: Message):
        if not message.text: return
        log(f"Новое сообщение от {message.peer_id}: {message.text[:20]}...")
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[message.text],
                config=types.GenerateContentConfig(
                    system_instruction="ты хамоватый гений, отвечай без заглавных букв"
                )
            )
            await message.answer(response.text)
            log("Ответ успешно отправлен.")
        except Exception as gem_err:
            log(f"ОШИБКА GEMINI: {gem_err}")
            await message.answer("нейронка тупит, попробуй позже.")

    log("БОТ ПОЛНОСТЬЮ ГОТОВ. ЗАПУСКАЮ RUN_FOREVER...")
    bot.run_forever()

except Exception:
    # Самый важный блок: если что-то пойдет не так, он распишет причину
    error_text = traceback.format_exc()
    log("!!! ПРОИЗОШЛА КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ !!!")
    print(error_text, flush=True)
    
    # Даем хостингу 10 секунд, чтобы он успел записать этот текст в логи перед тем, как всё сдохнет
    time.sleep(10)
    sys.exit(1)
