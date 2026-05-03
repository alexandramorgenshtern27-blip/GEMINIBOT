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

# Прокси
PROXY_URL = "http://Lp2dsp:SwUV5x@85.195.81.163:12213"
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

# Константы стиля
SYSTEM_PROMPT = (
    "Ты — дерзкий дрилл-подросток на чилл-вайбе. В чате пишешь строго маленькими буквами, "
    "без запятых и знаков препинания (кроме редких смайлов). Твой стиль — неформальный, "
    "но ты очень умный и отвечаешь на вопросы содержательно, как эксперт. "
    "Если тебя просят написать большой текст (эссе, доклад), пиши его СТРОГО официально, "
    "с соблюдением всех правил русского языка, грамотно и структурировано."
)

VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

def create_word_file(text):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    # Добавляем текст (разбивка по абзацам)
    for line in text.split('\n'):
        if line.strip():
            p = doc.add_paragraph(line)
            p.style = doc.styles['Normal']
            
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def upload_doc(vk, peer_id, file_stream, filename="answer.docx"):
    upload = vk_api.VkUpload(vk)
    doc_data = upload.document(file_stream, title=filename, target_peer_id=peer_id)
    return f"doc{doc_data['doc']['owner_id']}_{doc_data['doc']['id']}"

try:
    log("Запуск дрилл-бота...")
    client = genai.Client(api_key=GEMINI_KEY)
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    log("Система онлайн")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Запрос от {event.user_id}")
            
            # 1. Сразу реагируем, чтобы не молчать
            vk.messages.send(
                peer_id=event.peer_id,
                message="ща погодь чекну инфу по фасту...",
                random_id=int(time.time() * 1000)
            )

            try:
                # 2. Запрос к Gemini
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    config={'system_instruction': SYSTEM_PROMPT},
                    contents=event.text
                )
                
                full_text = response.text if response.text else "пусто чето бро"
                
                # 3. Решаем: текст или файл (граница 600 символов)
                if len(full_text) > 600:
                    log("Текст большой, пакуем в Word")
                    f_stream = create_word_file(full_text)
                    doc_attachment = upload_doc(vk_session, event.peer_id, f_stream)
                    
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message="короче там много вышло я в ворд закинул как ты любишь чекни файл",
                        attachment=doc_attachment,
                        random_id=int(time.time() * 1000)
                    )
                else:
                    # Обычный короткий ответ в стиле подростка
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message=full_text.lower().replace(",", ""),
                        random_id=int(time.time() * 1000)
                    )
                
                log("Ответ улетел")

            except Exception as e:
                log(f"Ошибка: {e}")
                vk.messages.send(
                    peer_id=event.peer_id,
                    message="бля чето серваки гугла легли по ходу сорян",
                    random_id=int(time.time() * 1000)
                )

except Exception as e:
    log(f"КРИТИЧЕСКИЙ СБОЙ: {e}")
    time.sleep(5)
    sys.exit(1)
