FROM python:3.11-slim

WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Запускаем бота с флагом -u (чтобы логи не застревали)
CMD ["python", "-u", "GEMINIVKBOT.py"]
