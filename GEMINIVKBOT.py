import os
import sys
import time
import requests # Нужен для изоляции прокси
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google import genai

def log(msg):
    print(f">>> [BOT-FINAL]: {msg}", flush=True)

# Данные твоего прокси
PROXY_URL = "http://Lp2dsp:SwUV5x@85.195.81.163:12213"

# Устанавливаем прокси ТОЛЬКО для библиотек, которые смотрят в систему (Gemini)
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

log("Старт системы. Настроены переменные для Gemini...")

VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

try:
    # 1. Настройка Gemini
    client = genai.Client(api_key=GEMINI_KEY)
    
    # 2. Настройка ВК (ГЛАВНЫЙ МОМЕНТ)
    # Создаем сессию, которая ИГНОРИРУЕТ системные прокси
    session = requests.Session()
    session.trust_env = False # Это заставит ВК работать напрямую
    
    vk_session = vk_api.VkApi(token=VK_TOKEN, session=session)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    
    log("ВК подключен напрямую. Gemini — через прокси.")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Запрос от {event.user_id}: {event.text[:15]}...")
            
            try:
                # Пробуем отправить запрос Gemini
                # Указываем модель без префикса 'models/', библиотека сама его добавит
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=event.text
                )
                
                answer = response.text if response.text else "Google прислал пустой ответ."
                
                vk.messages.send(
                    peer_id=event.peer_id,
                    message=answer,
                    random_id=int(time.time() * 1000)
                )
                log("Ответ отправлен.")
                
            except Exception as e:
                # Если 404 повторяется, попробуем альтернативное имя модели
                log(f"Ошибка Gemini: {e}")
                if "404" in str(e):
                    log("Пробую альтернативное имя модели...")
                    try:
                        response = client.models.generate_content(
                            model="gemini-1.5-flash-latest",
                            contents=event.text
                        )
                        vk.messages.send(
                            peer_id=event.peer_id,
                            message=response.text,
                            random_id=int(time.time() * 1000)
                        )
                    except:
                        pass

except Exception as e:
    log(f"КРИТИЧЕСКИЙ СБОЙ: {e}")
    time.sleep(10)
    sys.exit(1)
