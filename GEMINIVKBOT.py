import os
import sys
import time
import vk_api
import httpx
from vk_api.longpoll import VkLongPoll, VkEventType
from google import genai

def log(msg):
    print(f">>> [BOT-FINAL]: {msg}", flush=True)

# Твои данные из скриншота
PROXY_URL = "http://Lp2dsp:SwUV5x@85.195.81.163:12213"

log("Старт системы. Настраиваю прокси Германии...")

VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not VK_TOKEN or not GEMINI_KEY:
    log("ОШИБКА: Забыла добавить VK_TOKEN или GEMINI_KEY в панель хостинга!")
    sys.exit(1)

try:
    # Настройка клиента через прокси
    proxy_client = httpx.Client(proxies=PROXY_URL, timeout=30.0)
    
    # Инициализация Gemini
    client = genai.Client(
        api_key=GEMINI_KEY,
        http_options={'client': proxy_client}
    )
    
    # Автоматический выбор доступной модели
    log("Проверка доступности Gemini через прокси...")
    available_models = [m.name for m in client.models.list() if 'generateContent' in m.supported_methods]
    
    if not available_models:
        log("ОШИБКА: Google не отдал список моделей. Прокси не работает или забанен.")
        sys.exit(1)
        
    SELECTED_MODEL = available_models[0]
    log(f"Связь установлена! Использую модель: {SELECTED_MODEL}")

    # Инициализация ВК
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    log("Бот подключен к ВК и готов к общению!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Новое сообщение: {event.text[:20]}...")
            try:
                # Генерация ответа
                response = client.models.generate_content(
                    model=SELECTED_MODEL,
                    contents=event.text
                )
                
                final_text = response.text if response.text else "Google прислал пустой ответ."
                
                # Отправка в ВК
                vk.messages.send(
                    peer_id=event.peer_id,
                    message=final_text,
                    random_id=int(time.time() * 1000)
                )
                log("Ответ отправлен успешно.")
            except Exception as e:
                log(f"Ошибка Gemini: {e}")

except Exception as e:
    log(f"КРИТИЧЕСКИЙ СБОЙ: {e}")
    time.sleep(10)
    sys.exit(1)
