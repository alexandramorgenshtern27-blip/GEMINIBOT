import os
import sys
import time
import io
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google import genai
from docx import Document
from docx.shared import Pt

def log(msg):
    print(f">>> [BOT-FINAL]: {msg}", flush=True)

# --- НАСТРОЙКИ ---
PROXY_URL = "http://Lp2dsp:SwUV5x@85.195.81.163:12213"
VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

SYSTEM_PROMPT = (
    "ты дерзкий дрилл-подросток на чилл-вайбе. пишешь строго маленькими буквами, "
    "без запятых и точек. если просят написать что-то длинное — пиши это грамотно и официально."
)

try:
    log("Запуск системы. Настройка Gemini 2.0...")
    
    # Конфигурируем клиент Gemini с прокси сразу
    # Это решает проблему с доступом из РФ и корректно передает параметры
    client = genai.Client(
        api_key=GEMINI_KEY,
        http_options={'proxy': PROXY_URL}
    )

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    log("ВК и Gemini готовы!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Запрос от {event.user_id}")
            
            # Быстрый ответ, чтобы ВК не висел
            vk.messages.send(
                peer_id=event.peer_id,
                message="ща погодь чекну инфу по фасту...",
                random_id=int(time.time() * 1000)
            )

            try:
                # ВАЖНО: В новой библиотеке google-genai 
                # system_instruction передается внутри словаря config
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=event.text,
                    config={
                        'system_instruction': SYSTEM_PROMPT,
                    }
                )
                
                full_text = response.text if response.text else "пусто чето бро"
                
                if len(full_text) > 600:
                    # Создаем документ
                    doc = Document()
                    style = doc.styles['Normal']
                    font = style.font
                    font.name = 'Times New Roman'
                    font.size = Pt(12)
                    for line in full_text.split('\n'):
                        if line.strip(): doc.add_paragraph(line)
                    
                    f_stream = io.BytesIO()
                    doc.save(f_stream)
                    f_stream.seek(0)
                    
                    upload = vk_api.VkUpload(vk_session)
                    doc_data = upload.document(f_stream, title="answer.docx", target_peer_id=event.peer_id)
                    attachment = f"doc{doc_data['doc']['owner_id']}_{doc_data['doc']['id']}"
                    
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message="короче там много вышло я в ворд закинул чекни файл",
                        attachment=attachment,
                        random_id=int(time.time() * 1000)
                    )
                else:
                    # Дрилл-стайл форматирование
                    clean_text = full_text.lower().replace(",", "").replace(".", "").replace("!", "").replace("?", "")
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message=clean_text,
                        random_id=int(time.time() * 1000)
                    )
                log("Ответ отправлен")

            except Exception as e:
                log(f"Ошибка Gemini: {e}")
                vk.messages.send(
                    peer_id=event.peer_id,
                    message="бля чето гугл тупит сорян",
                    random_id=int(time.time() * 1000)
                )

except Exception as e:
    log(f"КРИТИЧЕСКИЙ СБОЙ: {e}")
    time.sleep(5)
    sys.exit(1)
