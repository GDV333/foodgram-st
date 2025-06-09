#!/bin/bash
# Скрипт для работы с Docker в разработке

set -e

# Определяем пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
INFRA_DIR="$PROJECT_ROOT/infra"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Функция помощи
show_help() {
    echo -e "${BLUE}=== Docker команды для Foodgram ===${NC}"
    echo ""
    echo "Использование: $0 [команда]"
    echo ""
    echo "Доступные команды:"
    echo -e "  ${GREEN}build${NC}     - Собрать Docker образы"
    echo -e "  ${GREEN}up${NC}        - Запустить контейнеры в фоне"
    echo -e "  ${GREEN}down${NC}      - Остановить и удалить контейнеры"
    echo -e "  ${GREEN}restart${NC}   - Перезапустить контейнеры"
    echo -e "  ${GREEN}logs${NC}      - Показать логи всех сервисов"
    echo -e "  ${GREEN}shell${NC}     - Войти в shell backend контейнера"
    echo -e "  ${GREEN}migrate${NC}   - Применить миграции Django"
    echo -e "  ${GREEN}collectstatic${NC} - Собрать статические файлы"
    echo -e "  ${GREEN}loaddata${NC}  - Загрузить фикстуры"
    echo -e "  ${GREEN}createsuperuser${NC} - Создать суперпользователя"
    echo -e "  ${GREEN}status${NC}    - Показать статус контейнеров"
    echo -e "  ${GREEN}clean${NC}     - Удалить все контейнеры и образы"
    echo ""
}

# Переходим в директорию с docker-compose
cd "$INFRA_DIR"

case "${1:-help}" in
    build)
        echo -e "${YELLOW}Сборка Docker образов...${NC}"
        docker-compose build
        ;;
    up)
        echo -e "${YELLOW}Запуск контейнеров...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✓ Контейнеры запущены!${NC}"
        echo -e "${YELLOW}Проверьте статус: $0 status${NC}"
        ;;
    down)
        echo -e "${YELLOW}Остановка контейнеров...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ Контейнеры остановлены${NC}"
        ;;
    restart)
        echo -e "${YELLOW}Перезапуск контейнеров...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ Контейнеры перезапущены${NC}"
        ;;
    logs)
        echo -e "${YELLOW}Логи всех сервисов:${NC}"
        docker-compose logs -f
        ;;
    shell)
        echo -e "${YELLOW}Вход в shell backend контейнера...${NC}"
        docker-compose exec backend bash
        ;;
    migrate)
        echo -e "${YELLOW}Применение миграций...${NC}"
        docker-compose exec backend python manage.py migrate
        ;;
    collectstatic)
        echo -e "${YELLOW}Сбор статических файлов...${NC}"
        docker-compose exec backend python manage.py collectstatic --no-input
        ;;
    loaddata)
        echo -e "${YELLOW}Загрузка фикстур...${NC}"
        docker-compose exec backend python manage.py loaddata ../fixtures/dev/ingredients_fixture.json
        docker-compose exec backend python manage.py create_test_data
        ;;
    createsuperuser)
        echo -e "${YELLOW}Создание суперпользователя...${NC}"
        docker-compose exec backend python manage.py createsuperuser
        ;;
    status)
        echo -e "${YELLOW}Статус контейнеров:${NC}"
        docker-compose ps
        echo ""
        echo -e "${YELLOW}Использование портов:${NC}"
        echo -e "  Frontend: ${GREEN}http://localhost:80${NC}"
        echo -e "  Backend API: ${GREEN}http://localhost:8000/api/${NC}"
        echo -e "  Admin: ${GREEN}http://localhost:8000/admin/${NC}"
        ;;
    clean)
        echo -e "${RED}Внимание! Это удалит ВСЕ контейнеры и образы проекта.${NC}"
        read -p "Продолжить? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Очистка Docker ресурсов...${NC}"
            docker-compose down -v --rmi all
            docker system prune -f
            echo -e "${GREEN}✓ Очистка завершена${NC}"
        else
            echo -e "${YELLOW}Операция отменена${NC}"
        fi
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Неизвестная команда: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
