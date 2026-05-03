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

# Твой прокси
PROXY_URL = "http://Lp2dsp:SwUV5x@85.195.81.163:12213"

SYSTEM_PROMPT = (
    "Ты — дерзкий дрилл-подросток на чилл-вайбе. В чате пишешь строго маленькими буквами, "
    "без запятых и знаков препинания. Твой стиль — неформальный, но ты очень умный. "
    "Если текст большой — пиши его официально и грамотно с соблюдением правил."
)

VK_TOKEN = os.environ.get("VK_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

def create_word_file(text):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    for line in text.split('\n'):
        if line.strip():
            doc.add_paragraph(line)
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def upload_doc(vk_session, peer_id, file_stream, filename="answer.docx"):
    upload = vk_api.VkUpload(vk_session)
    doc_data = upload.document(file_stream, title=filename, target_peer_id=peer_id)
    return f"doc{doc_data['doc']['owner_id']}_{doc_data['doc']['id']}"

try:
    log("Запуск системы. ВК напрямую, Gemini через инъекцию прокси...")
    
    # Инициализируем Gemini БЕЗ параметров прокси (чтобы не злить Pydantic)
    client = genai.Client(api_key=GEMINI_KEY)

    # Инициализируем ВК напрямую
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    log("ВК и Gemini готовы!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Запрос от {event.user_id}")
            
            vk.messages.send(
                peer_id=event.peer_id,
                message="ща погодь чекну инфу по фасту...",
                random_id=int(time.time() * 1000)
            )

            try:
                # --- ТАКТИКА НИНДЗЯ ВКЛЮЧЕНА ---
                os.environ["HTTP_PROXY"] = PROXY_URL
                os.environ["HTTPS_PROXY"] = PROXY_URL
                
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    config={'system_instruction': SYSTEM_PROMPT},
                    contents=event.text
                )
                
                # --- ТАКТИКА НИНДЗЯ ВЫКЛЮЧЕНА (чтобы LongPoll ВК не упал) ---
                if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
                if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]
                
                full_text = response.text if response.text else "пусто чето бро"
                
                if len(full_text) > 600:
                    f_stream = create_word_file(full_text)
                    doc_attachment = upload_doc(vk_session, event.peer_id, f_stream)
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message="короче там много вышло я в ворд закинул чекни файл",
                        attachment=doc_attachment,
                        random_id=int(time.time() * 1000)
                    )
                else:
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message=full_text.lower().replace(",", ""),
                        random_id=int(time.time() * 1000)
                    )
                log("Ответ доставлен")

            except Exception as e:
                # На случай ошибки тоже чистим переменные
                if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
                if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]
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
