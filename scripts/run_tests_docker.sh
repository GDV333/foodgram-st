#!/bin/bash
# Скрипт для запуска тестов API в Docker-контейнере

set -e

echo "🔄 Запуск тестов API Foodgram в контейнере..."

# Переходим в директорию с проектом
cd "$(dirname "$0")/.."

# Запускаем тесты в Docker-контейнере
docker-compose -f infra/docker-compose.yml run --rm backend python -m pytest

# Проверяем статус выполнения
if [ $? -eq 0 ]; then
  echo "✅ Все тесты выполнены успешно!"
else
  echo "❌ Тесты выполнены с ошибками."
  exit 1
fi
