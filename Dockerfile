FROM python:3.11-slim

# Ставим системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала ставим библиотеки, чтобы они закешировались
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Запускаем без буферизации логов
CMD ["python", "-u", "GEMINIVKBOT.py"]
