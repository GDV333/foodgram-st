#!/bin/bash
# Скрипт для запуска Newman тестов API Foodgram

set -e  # Остановить выполнение при ошибке

# Определяем пути относительно корня проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
POSTMAN_DIR="$PROJECT_ROOT/postman_collection"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Запуск Newman тестов Foodgram API ===${NC}"

# Проверяем наличие Newman
NEWMAN_CMD="newman"
if ! command -v newman &> /dev/null; then
    # Проверяем локальную установку Newman
    if [ -f "$PROJECT_ROOT/node_modules/.bin/newman" ]; then
        NEWMAN_CMD="$PROJECT_ROOT/node_modules/.bin/newman"
        echo -e "${GREEN}Используем локально установленный Newman${NC}"
    else
        echo -e "${RED}Ошибка: Newman не установлен. Установите его командой:${NC}"
        echo "cd $PROJECT_ROOT && npm install newman"
        exit 1
    fi
else
    echo -e "${GREEN}Используем глобально установленный Newman${NC}"
fi

# Проверяем доступность API (Docker или локальный сервер)
echo -e "${YELLOW}Проверка доступности API...${NC}"
API_AVAILABLE=false
USING_DOCKER=false

# Сначала проверяем Docker (localhost без порта)
if curl -s http://localhost/api/ingredients/ > /dev/null 2>&1; then
    echo -e "${GREEN}API доступно через Docker (http://localhost/api/)${NC}"
    API_AVAILABLE=true
    USING_DOCKER=true
# Затем проверяем локальный сервер (localhost:8000)
elif curl -s http://localhost:8000/api/ingredients/ > /dev/null 2>&1; then
    echo -e "${GREEN}API доступно через локальный сервер (http://localhost:8000/api/)${NC}"
    API_AVAILABLE=true
    USING_DOCKER=false
fi

if [ "$API_AVAILABLE" = false ]; then
    echo -e "${RED}Ошибка: API недоступно${NC}"
    echo "Запустите либо:"
    echo "  - Docker контейнеры: cd infra && docker-compose up -d"
    echo "  - Локальный сервер: ./scripts/dev/start_server.sh"
    exit 1
fi

# Переходим в директорию с Postman коллекцией
cd "$POSTMAN_DIR"

# Запускаем Newman тесты
echo -e "${YELLOW}Запуск Newman тестов...${NC}"

# Выбираем environment в зависимости от того, где запущен API
if [ "$USING_DOCKER" = true ]; then
    ENVIRONMENT_FILE="docker-environment.json"
    echo -e "${YELLOW}Используем Docker environment${NC}"
else
    # Создаем временный environment файл для локального сервера
    ENVIRONMENT_FILE="local-environment.json"
    echo -e "${YELLOW}Создаем временный environment для локального сервера${NC}"
    cat > "$ENVIRONMENT_FILE" << EOF
{
  "id": "local-environment",
  "name": "Local Environment",
  "values": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8000",
      "enabled": true
    }
  ]
}
EOF
fi

$NEWMAN_CMD run foodgram.postman_collection.json \
    --environment "$ENVIRONMENT_FILE" \
    --reporters cli,junit \
    --reporter-junit-export newman-results.xml \
    --timeout-request 10000 \
    --delay-request 100

# Удаляем временный environment файл если он был создан
if [ "$USING_DOCKER" = false ] && [ -f "$ENVIRONMENT_FILE" ]; then
    rm "$ENVIRONMENT_FILE"
fi

# Сохраняем код выхода Newman
NEWMAN_EXIT_CODE=$?

# Деактивируем виртуальное окружение
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
    echo -e "${GREEN}✓ Виртуальное окружение деактивировано${NC}"
fi

echo -e "${YELLOW}Очищаем тестовых пользователей...${NC}"
cd "$PROJECT_ROOT"

# Выбираем способ очистки в зависимости от того, где запущен API
if [ "$USING_DOCKER" = true ]; then
    echo -e "${YELLOW}Используем Docker команду для очистки...${NC}"
    make docker-clear-test-users
else
    echo -e "${YELLOW}Используем команду для локального сервера...${NC}"
    make clear-test-users
fi

if [ $NEWMAN_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Newman тесты завершены успешно!${NC}"
else
    echo -e "${RED}❌ Newman тесты завершены с ошибками (код: $NEWMAN_EXIT_CODE)${NC}"
    echo -e "${YELLOW}Результаты сохранены в: $POSTMAN_DIR/newman-results.xml${NC}"
fi

exit $NEWMAN_EXIT_CODE
