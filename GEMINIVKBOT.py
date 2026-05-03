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
    log("ОШИБКА: Забыла добавить VK_TOKEN или GEMINI_KEY в панель хоста!")
    sys.exit(1)

try:
    # ИСПРАВЛЕННЫЙ БЛОК: убран 's' в слове proxy
    proxy_client = httpx.Client(proxy=PROXY_URL, timeout=30.0)
    
    client = genai.Client(
        api_key=GEMINI_KEY,
        http_options={'client': proxy_client}
    )
    
    log("Проверка доступности Gemini через прокси...")
    available_models = [m.name for m in client.models.list() if 'generateContent' in m.supported_methods]
    
    if not available_models:
        log("ОШИБКА: Список моделей пуст.")
        sys.exit(1)
        
    SELECTED_MODEL = available_models[0]
    log(f"Связь установлена! Модель: {SELECTED_MODEL}")

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    log("Бот подключен к ВК!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Новое сообщение: {event.text[:20]}...")
            try:
                response = client.models.generate_content(
                    model=SELECTED_MODEL,
                    contents=event.text
                )
                vk.messages.send(
                    peer_id=event.peer_id,
                    message=response.text or "...",
                    random_id=int(time.time() * 1000)
                )
                log("Ответ отправлен.")
            except Exception as e:
                log(f"Ошибка Gemini: {e}")

except Exception as e:
    log(f"КРИТИЧЕСКИЙ СБОЙ: {e}")
    time.sleep(10)
    sys.exit(1)
