#!/bin/bash
# Скрипт для установки зависимостей проекта

set -e

# Определяем пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Установка зависимостей проекта Foodgram ===${NC}"

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не установлен"
    exit 1
fi

# Проверяем наличие Node.js для Newman
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Внимание: Node.js не установлен. Newman тесты будут недоступны.${NC}"
    echo "Установите Node.js для запуска API тестов"
else
    echo -e "${GREEN}✓ Node.js найден: $(node --version)${NC}"
fi

# Переходим в директорию backend
cd "$BACKEND_DIR"

# Создаем виртуальное окружение
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Создание виртуального окружения...${NC}"
    python3 -m venv .venv
fi

# Активируем виртуальное окружение
source .venv/bin/activate

# Обновляем pip
echo -e "${YELLOW}Обновление pip...${NC}"
pip install --upgrade pip

# Устанавливаем зависимости Python
echo -e "${YELLOW}Установка зависимостей Python...${NC}"
pip install -r requirements.txt

# Устанавливаем Newman если доступен npm
if command -v npm &> /dev/null; then
    echo -e "${YELLOW}Установка Newman для API тестов...${NC}"
    cd "$PROJECT_ROOT"
    # Устанавливаем Newman локально в проект
    npm install newman
    echo -e "${GREEN}✓ Newman установлен локально${NC}"
fi

echo -e "${GREEN}✅ Все зависимости установлены успешно!${NC}"
echo -e "${BLUE}Следующие шаги:${NC}"
echo -e "  1. Сброс базы данных: ${YELLOW}./scripts/dev/reset_db.sh${NC}"
echo -e "  2. Запуск сервера: ${YELLOW}./scripts/dev/start_server.sh${NC}"
echo -e "  3. Запуск тестов: ${YELLOW}./scripts/tests/run_pytest.py${NC}"
echo -e "  4. Запуск API тестов: ${YELLOW}./scripts/tests/run_newman.sh${NC}"
