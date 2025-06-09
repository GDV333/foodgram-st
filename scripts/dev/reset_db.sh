#!/bin/bash
# Скрипт для сброса базы данных и создания тестовых данных

set -e

# Определяем пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Сброс базы данных и создание тестовых данных ===${NC}"

# Переходим в директорию backend
cd "$BACKEND_DIR"

# Активируем виртуальное окружение если есть
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Удаляем базу данных SQLite (если используется)
if [ -f "db.sqlite3" ]; then
    echo -e "${YELLOW}Удаление старой базы данных...${NC}"
    rm db.sqlite3
fi

# Удаляем только пользовательские файлы миграций (не системные Django)
echo -e "${YELLOW}Очистка пользовательских миграций...${NC}"
find api/migrations/ -name "*.py" -not -name "__init__.py" -delete 2>/dev/null || true
find recipes/migrations/ -name "*.py" -not -name "__init__.py" -delete 2>/dev/null || true  
find users/migrations/ -name "*.py" -not -name "__init__.py" -delete 2>/dev/null || true
find . -path "*/migrations/*.pyc" -delete 2>/dev/null || true

# Создаем новые миграции
echo -e "${YELLOW}Создание миграций...${NC}"
python manage.py makemigrations

# Применяем миграции
echo -e "${YELLOW}Применение миграций...${NC}"
python manage.py migrate

# Загружаем ингредиенты
echo -e "${YELLOW}Загрузка ингредиентов...${NC}"
if [ -f "../fixtures/dev/ingredients_fixture.json" ]; then
    python manage.py loaddata ../fixtures/dev/ingredients_fixture.json
else
    echo -e "${RED}Файл ингредиентов не найден: ../fixtures/dev/ingredients_fixture.json${NC}"
fi

# Создаем базовые данные (только ингредиенты, без пользователей)
echo -e "${YELLOW}Создание базовых данных для Newman тестов...${NC}"
python manage.py create_test_data

echo -e "${GREEN}✅ База данных готова для Newman тестов!${NC}"
echo -e "${GREEN}Созданы только базовые данные (ингредиенты)${NC}"
echo -e "${YELLOW}Пользователи и рецепты будут созданы Newman тестами через API${NC}"
