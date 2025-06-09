FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала копируем только requirements.txt для кеширования слоя
COPY requirements.txt .

# Устанавливаем Python зависимости (этот слой будет кешироваться)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Теперь копируем остальные файлы
COPY . .

# Создаем директории для статики и медиа
RUN mkdir -p /app/static /app/media

# Собираем статику (без миграций в Dockerfile)
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
