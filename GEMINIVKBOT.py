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
# Если ты уже прописал прокси в настройках хостинга, эти строки ниже можно не менять.
# Они просто подстрахуют, если на хосте что-то не подхватилось.
PROXY_URL = "http://Lp2dsp:SwUV5x@85.195.81.163:12213"
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

SYSTEM_PROMPT = (
    "ты дерзкий дрилл-подросток на чилл-вайбе. пишешь строго маленькими буквами, "
    "без запятых и точек. если просят написать что-то длинное — пиши это грамотно и официально."
)

try:
    log("Запуск системы. Настройка Gemini 2.0...")
    
    # КРИТИЧЕСКИЙ МОМЕНТ: 
    # В скобках ниже должен быть ТОЛЬКО api_key. 
    # Никаких http_options или proxy, иначе будет ошибка Pydantic!
    client = genai.Client(api_key=GEMINI_KEY)

    # Инициализируем ВК
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    log("ВК и Gemini 2.0 готовы!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Запрос от {event.user_id}")
            
            vk.messages.send(
                peer_id=event.peer_id,
                message="ща погодь чекну инфу по фасту...",
                random_id=int(time.time() * 1000)
            )

            try:
                # Генерируем ответ
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=event.text,
                    config={
                        'system_instruction': SYSTEM_PROMPT,
                    }
                )
                
                full_text = response.text if response.text else "пусто чето бро"
                
                if len(full_text) > 600:
                    doc = Document()
                    # Упрощенная запись в ворд
                    p = doc.add_paragraph(full_text)
                    p.style.font.name = 'Times New Roman'
                    p.style.font.size = Pt(12)
                    
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
                    # Убираем знаки препинания для чилл-вайба
                    clean_text = full_text.lower().replace(",", "").replace(".", "").replace("!", "").replace("?", "")
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message=clean_text,
                        random_id=int(time.time() * 1000)
                    )
                log("Ответ доставлен")

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
