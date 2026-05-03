import os
import sys
import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google import genai

def log(msg):
    print(f">>> [LIGHT-BOT]: {msg}", flush=True)

log("Запуск облегченной версии...")

# Получаем ключи
VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not VK_TOKEN or not GEMINI_KEY:
    log("Ошибка: нет ключей в переменных!")
    sys.exit(1)

try:
    # Авторизация ВК
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    
    # Авторизация Gemini
    client = genai.Client(api_key=GEMINI_KEY)
    
    log("Связь с ВК и Gemini установлена. Жду сообщений...")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Пришло сообщение: {event.text[:30]}")
            
            try:
                # Запрос к нейронке
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[event.text]
                )
                
                # Отправка ответа в ВК
                vk.messages.send(
                    peer_id=event.peer_id,
                    message=response.text,
                    random_id=int(time.time() * 1000)
                )
                log("Ответ отправлен.")
                
            except Exception as e:
                log(f"Ошибка Gemini или ВК: {e}")

except Exception as e:
    log(f"Критическая ошибка: {e}")
    time.sleep(5)
    sys.exit(1)
