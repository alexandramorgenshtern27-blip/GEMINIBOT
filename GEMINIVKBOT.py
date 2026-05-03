import os
import sys
import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google import genai

def log(msg):
    print(f">>> [BOT]: {msg}", flush=True)

log("Запуск... Проверяю окружение.")

# 1. Загрузка ключей из переменных хостинга
VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not VK_TOKEN or not GEMINI_KEY:
    log("КРИТИЧЕСКАЯ ОШИБКА: Проверь VK_TOKEN и GEMINI_KEY в панели хоста!")
    sys.exit(1)

try:
    # 2. Инициализация Gemini
    client = genai.Client(api_key=GEMINI_KEY)
    
    # Автоматически ищем первую доступную модель, чтобы не гадать с именами
    log("Ищу доступные модели Gemini...")
    available_models = [m.name for m in client.models.list() if 'generateContent' in m.supported_methods]
    
    if not available_models:
        log("ОШИБКА: Твой ключ не поддерживает ни одну модель!")
        sys.exit(1)
    
    # Берем самую первую (обычно это 1.5-flash)
    SELECTED_MODEL = available_models[0]
    log(f"Буду использовать модель: {SELECTED_MODEL}")

    # 3. Авторизация ВК
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    log("Бот успешно подключился к ВК.")

    # 4. Основной цикл
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Сообщение от {event.user_id}: {event.text[:20]}...")
            
            try:
                # Запрос к нейронке
                response = client.models.generate_content(
                    model=SELECTED_MODEL,
                    contents=event.text
                )
                
                # Проверка на пустой ответ
                answer = response.text if response.text else "эм... я не знаю что ответить"
                
                # Отправка в ВК
                vk.messages.send(
                    user_id=event.user_id,
                    message=answer,
                    random_id=int(time.time() * 1000)
                )
                log("Ответ отправлен.")

            except Exception as e:
                log(f"Ошибка при обработке запроса: {e}")
                # Если Google ругается на квоту (429), бот просто подождет
                if "429" in str(e):
                    time.sleep(5)

except Exception as e:
    log(f"Критический сбой: {e}")
    time.sleep(10)
    sys.exit(1)
