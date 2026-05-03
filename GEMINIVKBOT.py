import os
import sys
import time
import vk_api
import httpx
from vk_api.longpoll import VkLongPoll, VkEventType
from google import genai

def log(msg):
    print(f">>> [BOT-FINAL]: {msg}", flush=True)

# Твои данные прокси
PROXY_URL = "http://Lp2dsp:SwUV5x@85.195.81.163:12213"

log("Старт системы. Настройка раздельных каналов...")

VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

try:
    # 1. Настройка Gemini через изолированный httpx клиент
    # Мы не пишем в os.environ, чтобы не мешать ВК
    log("Подключаю Gemini через прокси...")
    
    # Создаем транспорт с прокси
    # В новой версии httpx используем аргумент proxy
    with httpx.Client(proxy=PROXY_URL, timeout=60.0) as proxy_client:
        
        client = genai.Client(
            api_key=GEMINI_KEY,
            http_options={'client': proxy_client}
        )

        # 2. Настройка ВК (полностью напрямую)
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        log("ВК и Gemini настроены раздельно!")

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                log(f"Запрос от {event.user_id}")
                
                try:
                    # Запрос к нейронке
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=event.text
                    )
                    
                    answer = response.text if response.text else "Google молчит..."
                    
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message=answer,
                        random_id=int(time.time() * 1000)
                    )
                    log("Ответ доставлен!")
                    
                except Exception as e:
                    log(f"Ошибка Gemini: {e}")
                    # Если прокси IPv6 не тянет, бот не упадет, а напишет ошибку в консоль

except Exception as e:
    log(f"КРИТИЧЕСКИЙ СБОЙ: {e}")
    time.sleep(10)
    sys.exit(1)
