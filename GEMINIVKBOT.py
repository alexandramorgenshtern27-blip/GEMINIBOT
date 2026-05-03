import os
import sys
import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google import genai

def log(msg):
    print(f">>> [BOT-FINAL]: {msg}", flush=True)

# Твои данные прокси
PROXY_URL = "http://Lp2dsp:SwUV5x@85.195.81.163:12213"

# Системные переменные для прокси
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

log("Старт системы. Прокси настроены.")

VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not VK_TOKEN or not GEMINI_KEY:
    log("ОШИБКА: Нет ключей VK_TOKEN или GEMINI_KEY!")
    sys.exit(1)

try:
    # Инициализация клиента
    client = genai.Client(api_key=GEMINI_KEY)
    
    # Прямая проверка связи с Google
    log("Проверяю связь с Google Gemini...")
    try:
        # Просто пробуем отправить тестовый запрос
        test_res = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="test"
        )
        log("Связь с Gemini УСТАНОВЛЕНА!")
    except Exception as e:
        log(f"Ошибка проверки связи (возможно, прокси): {e}")
        # Не выходим, пробуем работать дальше

    # Подключаем ВК
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    log("Бот подключен к ВК!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Сообщение от {event.user_id}")
            try:
                # Используем проверенную модель напрямую
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=event.text
                )
                
                answer = response.text if response.text else "Нейронка не ответила."
                
                vk.messages.send(
                    peer_id=event.peer_id,
                    message=answer,
                    random_id=int(time.time() * 1000)
                )
                log("Ответ отправлен.")
            except Exception as e:
                log(f"Ошибка при генерации: {e}")

except Exception as e:
    log(f"КРИТИЧЕСКИЙ СБОЙ: {e}")
    time.sleep(10)
    sys.exit(1)
