import os
import sys
# Эти импорты настроены под твою версию vkbottle
from vkbottle import Bot, Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Message 
from google import genai
from google.genai import types

def log(msg):
    print(f"--- {msg} ---", flush=True)

# 1. Пытаемся достать ключи из переменных окружения
VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

# 2. Жесткая проверка: если ключей нет, бот даже не дернется
if not VK_TOKEN or not GEMINI_KEY:
    log("ОШИБКА: Ключи не найдены в переменных хостинга!")
    log("Проверь вкладку Environment Variables в панели управления.")
    sys.exit(1)

log("Ключи получены из системы. Запускаю модули...")

try:
    # Инициализация клиента Gemini и Бота ВК
    client = genai.Client(api_key=GEMINI_KEY)
    bot = Bot(token=VK_TOKEN)
    log("Подключение к API успешно")
except Exception as e:
    log(f"Ошибка инициализации: {e}")
    sys.exit(1)

@bot.on.message()
async def handler(message: Message):
    if not message.text:
        return
    
    log(f"Пришло сообщение: {message.text[:20]}...")
    
    try:
        # Запрос к нейронке
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[message.text],
            config=types.GenerateContentConfig(
                system_instruction="ты хамоватый гений, отвечай дерзко, кратко и без заглавных букв"
            )
        )
        # Отправка ответа пользователю
        await message.answer(response.text)
        log("Ответ отправлен в ВК")
    except Exception as e:
        log(f"Ошибка при генерации: {e}")
        await message.answer("блин, че-то я приуныл. попробуй еще раз.")

if __name__ == "__main__":
    log("БОТ ВЫШЕЛ В СЕТЬ (LONGPOLL)")
    bot.run_forever()
