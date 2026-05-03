FROM python:3.11-slim

# Оптимизация Python для работы в малых контейнерах
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Копируем и ставим всё сразу
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск с ограничением воркеров (чтобы не плодить процессы)
CMD ["python", "-u", "GEMINIVKBOT.py"]
