# Gemini VK Bot

VK-бот на `vkbottle` с интеграцией:
- Google Gemini (`google-genai`) для текстовых ответов;
- Hugging Face Inference API для генерации изображений;
- экспорт ответа в `.docx`.

## 1) Подготовка окружения

1. Скопируй шаблон:
   - `cp .env.example .env` (Linux/Mac)
   - `copy .env.example .env` (Windows CMD)
2. Заполни `.env`:
   - `VK_TOKEN`
   - `GEMINI_KEY`
   - `HF_TOKEN`

## 2) Локальный запуск

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/Mac:
# source .venv/bin/activate

pip install -r requirements.txt
python GEMINIVKBOT.py
```

## 3) Docker запуск

```bash
docker build -t gemini-vk-bot .
docker run --env-file .env --name gemini-vk-bot --restart unless-stopped gemini-vk-bot
```

## 4) Быстрый деплой на хост (чтобы просто заработало)

1. Загрузи проект в GitHub (весь репозиторий).
2. На хосте создай сервис из Dockerfile/репозитория.
3. Тип процесса: `worker` (не `web`).
4. Команда запуска (если поле есть): `python -u GEMINIVKBOT.py`
   - если поле пустое, будет использована команда из `Dockerfile`.
5. Добавь переменные окружения:
   - `VK_TOKEN=...`
   - `GEMINI_KEY=...`
   - `HF_TOKEN=...`
6. Нажми `Redeploy` / `Restart`.
7. Открой `Runtime logs` / `Container logs`.

В логах должны быть строки:
- `Booting GeminiVKBOT container process`
- `--- БОТ ЗАПУЩЕН И ГОТОВ ХАМИТЬ ---`

Если есть ошибка, в логах теперь будет полный traceback с причиной.
Если панель логов хоста пустая, открой Web Terminal и проверь файл:

```bash
cat /app/data/startup_error.log
```

Этот файл заполняется автоматически при фатальных ошибках старта.

## 5) Публикация на GitHub

```bash
git init
git add .
git commit -m "Prepare project for GitHub and Docker deployment"
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

## Важно по безопасности

- Никогда не коммить `.env` и токены.
- Если токены уже светились в коде/чате — перевыпусти их в кабинетах VK/Gemini/Hugging Face.
