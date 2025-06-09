#!/bin/bash
# Скрипт для запуска Django сервера разработки

set -e

# Определяем пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Запуск Django сервера разработки ===${NC}"

# Переходим в директорию backend
cd "$BACKEND_DIR"

# Проверяем наличие виртуального окружения
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    echo -e "${YELLOW}Создание виртуального окружения...${NC}"
    python3 -m venv .venv
fi

# Активируем виртуальное окружение
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Устанавливаем зависимости
echo -e "${YELLOW}Проверка зависимостей...${NC}"
pip install -q -r requirements.txt

# Применяем миграции
echo -e "${YELLOW}Применение миграций...${NC}"
python manage.py migrate

# Загружаем базовые данные (ингредиенты)
echo -e "${YELLOW}Загрузка базовых данных...${NC}"
if [ -f "../data/ingredients_fixture.json" ]; then
    python manage.py loaddata ../data/ingredients_fixture.json
fi

# Запускаем сервер
echo -e "${GREEN}✓ Запуск Django сервера на http://localhost:8000${NC}"
python manage.py runserver
