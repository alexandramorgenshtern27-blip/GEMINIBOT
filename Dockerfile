FROM python:3.11-slim

# Настройка окружения для экономии памяти
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Устанавливаем системные зависимости (нужны для некоторых либ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем только требования и ставим их
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Запуск с принудительным выводом логов
CMD ["python", "-u", "GEMINIVKBOT.py"]
