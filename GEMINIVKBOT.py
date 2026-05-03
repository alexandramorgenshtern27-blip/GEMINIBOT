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

# Промпт для характера (дрилл-подросток)
SYSTEM_PROMPT = (
    "ты дерзкий дрилл-подросток на чилл-вайбе. пишешь строго маленькими буквами, "
    "без запятых и точек. общаешься неформально, используешь сленг, но при этом ты "
    "очень умный и реально помогаешь с инфой. если просят написать что-то длинное "
    "(эссе или доклад) — пиши это грамотно, официально и со всеми знаками препинания."
)

# --- ФУНКЦИИ ---

def create_word_file(text):
    """Создает Word файл: Times New Roman, 12pt"""
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
    """Загружает файл в ВК"""
    upload = vk_api.VkUpload(vk_session)
    doc_data = upload.document(file_stream, title=filename, target_peer_id=peer_id)
    return f"doc{doc_data['doc']['owner_id']}_{doc_data['doc']['id']}"

# --- ОСНОВНОЙ ЦИКЛ ---

try:
    log("Запуск системы. Настройка раздельных каналов...")
    
    # Инициализируем клиент Gemini
    client = genai.Client(api_key=GEMINI_KEY)

    # Инициализируем ВК напрямую
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    log("ВК и Gemini готовы к работе!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            log(f"Запрос от {event.user_id}: {event.text[:20]}...")
            
            # Сразу отвечаем пользователю, чтобы не молчать
            vk.messages.send(
                peer_id=event.peer_id,
                message="ща погодь чекну инфу по фасту...",
                random_id=int(time.time() * 1000)
            )

            try:
                # Включаем прокси только на время запроса к Google
                os.environ["HTTP_PROXY"] = PROXY_URL
                os.environ["HTTPS_PROXY"] = PROXY_URL
                
                # Запрос к нейронке (используем стабильную версию модели)
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    config={'system_instruction': SYSTEM_PROMPT},
                    contents=event.text
                )
                
                # Выключаем прокси сразу после ответа
                if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
                if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]
                
                full_text = response.text if response.text else "чето пусто бро сорян"
                
                # Проверяем длину: если больше 600 символов — шлем файл
                if len(full_text) > 600:
                    log("Текст большой, создаю Word...")
                    f_stream = create_word_file(full_text)
                    doc_attach = upload_doc(vk_session, event.peer_id, f_stream)
                    
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message="короче там дофига вышло я в ворд всё закинул чекни файл ниже",
                        attachment=doc_attach,
                        random_id=int(time.time() * 1000)
                    )
                else:
                    # Маленький ответ: убираем запятые и в нижний регистр
                    final_msg = full_text.lower().replace(",", "").replace(".", "")
                    vk.messages.send(
                        peer_id=event.peer_id,
                        message=final_msg,
                        random_id=int(time.time() * 1000)
                    )
                
                log("Ответ успешно отправлен!")

            except Exception as e:
                # Очистка прокси при ошибке
                if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
                if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]
                log(f"Ошибка Gemini: {e}")
                vk.messages.send(
                    peer_id=event.peer_id,
                    message="бля чето гугл затупил или прокси сдохли сорян",
                    random_id=int(time.time() * 1000)
                )

except Exception as e:
    log(f"КРИТИЧЕСКИЙ СБОЙ: {e}")
    time.sleep(5)
    sys.exit(1)
