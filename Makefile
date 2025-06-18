# Makefile для удобства запуска команд проекта Foodgram

.PHONY: help install dev-setup dev-start dev-reset test test-api test-unit \
        docker-build docker-up docker-down clean lint format check-all docs \
        setup full-setup quick-start production create-env load-data \
        clear-test-users

# По умолчанию показываем справку
help:
	@echo "🍽️  Makefile для проекта Foodgram"
	@echo ""
	@echo "📋 Основные команды для запуска:"
	@echo ""
	@echo "🚀 Быстрый старт:"
	@echo "  setup        - 🎯 ПОЛНАЯ НАСТРОЙКА ПРОЕКТА (рекомендуется)"
	@echo "  quick-start  - ⚡ Быстрый запуск (если уже настроено)"
	@echo "  production   - 🏭 Запуск в production режиме"
	@echo ""
	@echo "📊 Управление данными:"
	@echo "  create-env   - Создать .env файл из примера"
	@echo "  load-data    - Загрузить данные ингредиентов"
	@echo "  dev-reset    - Сбросить БД и создать тестовые данные"
	@echo ""
	@echo "🔧 Разработка:"
	@echo "  install      - Установить все зависимости"
	@echo "  dev-setup    - Подготовить окружение разработки"
	@echo "  dev-start    - Запустить Django сервер разработки"
	@echo ""
	@echo "🧪 Тестирование:"
	@echo "  test         - Запустить все тесты"
	@echo "  test-unit    - Запустить unit тесты (pytest)"
	@echo "  test-api     - Запустить API тесты (Newman)"
	@echo "  test-coverage- Запустить тесты с покрытием"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-build - Собрать Docker образы"
	@echo "  docker-up    - Запустить в Docker"
	@echo "  docker-down  - Остановить Docker контейнеры"
	@echo "  docker-clear-test-users - Очистить тестовых пользователей Newman (Docker)"
	@echo ""
	@echo "🧪 Очистка тестовых данных:"
	@echo "  clear-test-users - Очистить тестовых пользователей Newman (локальный сервер)"
	@echo ""
	@echo "🔧 Утилиты:"
	@echo "  lint         - Проверить код линтерами"
	@echo "  format       - Отформатировать код"
	@echo "  check-all    - Выполнить все проверки"
	@echo "  clean        - Очистить временные файлы"
	@echo "  docs         - Открыть документацию API"

# === ГЛАВНЫЕ КОМАНДЫ ДЛЯ ЗАПУСКА ===

setup: create-env install dev-setup load-data
	@echo ""
	@echo "🎉 ПРОЕКТ ПОЛНОСТЬЮ НАСТРОЕН!"
	@echo ""
	@echo "🚀 Для запуска используйте:"
	@echo "   make quick-start    - для разработки"
	@echo "   make production     - для production"
	@echo ""

quick-start: 
	@echo "⚡ Быстрый запуск проекта..."
	@if [ ! -f "infra/.env" ]; then echo "❌ Не найден infra/.env файл. Запустите: make create-env"; exit 1; fi
	@echo "🚀 Запускаем Django сервер..."
	./scripts/dev/start_server.sh

production: create-env docker-build docker-up
	@echo ""
	@echo "🏭 Production запущен!"
	@echo "📖 API документация: http://localhost/api/docs/"
	@echo "🔧 Админка: http://localhost/admin/"
	@echo ""

create-env:
	@echo "🔧 Создание .env файлов..."
	@if [ ! -f "infra/.env" ]; then \
		cp .env.example infra/.env && \
		echo "✅ Создан infra/.env из .env.example"; \
	else \
		echo "ℹ️  infra/.env уже существует"; \
	fi
	@echo "🔧 Настройте infra/.env под ваши нужды"

load-data:
	@echo "📊 Загрузка данных ингредиентов..."
	@cd backend && .venv/bin/python manage.py loaddata ../fixtures/dev/ingredients_fixture.json || \
	cd backend && .venv/bin/python manage.py shell -c "from recipes.models import Ingredient; import json; ingredients = json.load(open('../data/ingredients.json')); [Ingredient.objects.get_or_create(name=i['name'], measurement_unit=i['measurement_unit']) for i in ingredients]; print('✅ Ингредиенты загружены')"

# === Команды разработки ===

install:
	@echo "📦 Установка зависимостей..."
	@echo "🔍 Проверяем Node.js для Newman тестов..."
	@which node > /dev/null || (echo "❌ Node.js не найден. Установите Node.js для Newman тестов." && exit 1)
	@echo "📥 Устанавливаем Newman..."
	npm install
	@echo "🐍 Устанавливаем Python зависимости..."
	./scripts/dev/install_deps.sh
	@echo "✅ Все зависимости установлены!"

dev-setup: install 
	@echo "🔧 Настройка окружения разработки..."
	@cd backend && .venv/bin/python manage.py migrate
	@echo "👤 Создание суперпользователя (если нужен)..."
	@cd backend && echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | .venv/bin/python manage.py shell || true
	@echo "✅ Окружение разработки настроено!"

dev-start:
	@echo "🚀 Запуск Django сервера разработки..."
	@echo "📍 Сервер будет доступен на http://127.0.0.1:8000/"
	@echo "🔧 Админка: http://127.0.0.1:8000/admin/ (admin/admin)"
	@echo "📖 API docs: http://127.0.0.1:8000/api/docs/"
	./scripts/dev/start_server.sh

dev-reset:
	@echo "🔄 Полный сброс базы данных..."
	./scripts/dev/reset_db.sh
	@echo "📊 Загружаем ингредиенты..."
	@make load-data
	@echo "✅ База данных сброшена и данные загружены!"

# === Команды тестирования ===

test: test-unit test-api
	@echo "✅ Все тесты выполнены!"

test-unit:
	@echo "🧪 Запуск unit тестов..."
	./scripts/tests/run_pytest.py

test-api:
	@echo "🌐 Запуск API тестов..."
	./scripts/tests/run_newman.sh

test-coverage:
	@echo "📊 Запуск тестов с покрытием..."
	./scripts/tests/run_pytest.py --coverage

# === Docker команды ===

docker-build:
	@echo "🐳 Сборка Docker образов..."
	@if [ ! -f "infra/.env" ]; then echo "❌ Создайте infra/.env файл: make create-env"; exit 1; fi
	cd infra && docker compose build --no-cache
	@echo "✅ Docker образы собраны!"

docker-up:
	@echo "🐳 Запуск в Docker режиме..."
	@if [ ! -f "infra/.env" ]; then echo "❌ Создайте infra/.env файл: make create-env"; exit 1; fi
	cd infra && docker compose up -d
	@echo "⏳ Ждем запуска контейнеров..."
	@sleep 10
	@echo "📊 Применяем миграции..."
	cd infra && docker compose exec backend python manage.py migrate || true
	@echo "📦 Загружаем данные..."
	cd infra && docker compose exec backend python manage.py loaddata fixtures/dev/ingredients_fixture.json || true
	@echo "👤 Создаем суперпользователя..."
	cd infra && docker compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')" || true
	@echo ""
	@echo "🎉 Docker контейнеры запущены!"
	@echo "🌐 Фронтенд: http://localhost/"
	@echo "📖 API docs: http://localhost/api/docs/"
	@echo "🔧 Админка: http://localhost/admin/ (admin/admin)"
	@echo ""

docker-down:
	@echo "🐳 Остановка Docker контейнеров..."
	cd infra && docker compose down
	@echo "✅ Контейнеры остановлены!"

docker-clean:
	@echo "🧹 Очистка Docker (volumes, images)..."
	cd infra && docker compose down -v
	docker system prune -f
	@echo "✅ Docker очищен!"

docker-restart:
	@echo "🔄 Быстрый перезапуск Docker (с сохранением данных)..."
	cd infra && docker compose down
	cd infra && docker compose up -d --build
	@echo "⏳ Ждем запуска контейнеров..."
	@sleep 15
	@echo "📊 Применяем миграции..."
	cd infra && docker compose exec backend python manage.py migrate || true
	@echo "✅ Перезапуск завершен!"

docker-full-restart: docker-clean docker-build docker-up
	@echo "🔄 Полный перезапуск с очисткой данных завершен!"

docker-load-fixtures:
	@echo "📦 Загрузка фикстур в production..."
	cd infra && docker compose exec backend python manage.py loaddata fixtures/dev/ingredients_fixture.json
	@echo "✅ Фикстуры загружены!"

docker-create-superuser:
	@echo "👤 Создание суперпользователя..."
	cd infra && docker compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"
	@echo "✅ Суперпользователь создан (admin/admin)!"

docker-clear-users:
	@echo "🗑️ Очистка пользователей (кроме суперпользователей)..."
	cd infra && docker compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=False).delete(); print('✅ Обычные пользователи удалены')"

docker-clear-test-users:
	@echo "🧪 Очистка тестовых пользователей Newman..."
	cd infra && docker compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); usernames_list = ['vasya.ivanov', 'second-user', 'third-user-username', 'NoEmail', 'NoFirstName', 'NoLastName', 'NoPassword', 'TooLongEmail', 'the-username-that-is-150-characters-long-and-should-not-pass-validation-if-the-serializer-is-configured-correctly-otherwise-the-current-test-will-fail-', 'TooLongFirstName', 'TooLongLastName', 'InvalidU\$$ername', 'EmailInUse']; deleted_count, _ = User.objects.filter(username__in=usernames_list).delete(); print(f'✅ Удалено {deleted_count} тестовых пользователей')"

docker-clear-recipes:
	@echo "🗑️ Очистка всех рецептов..."
	cd infra && docker compose exec backend python manage.py shell -c "from recipes.models import Recipe; Recipe.objects.all().delete(); print('✅ Все рецепты удалены')"

docker-clear-all-data:
	@echo "🗑️ ПОЛНАЯ очистка всех данных (кроме ингредиентов и суперпользователей)..."
	cd infra && docker compose exec backend python manage.py shell -c "from recipes.models import Recipe; from django.contrib.auth import get_user_model; User = get_user_model(); Recipe.objects.all().delete(); User.objects.filter(is_superuser=False).delete(); print('✅ Данные очищены')"
	@echo "⚠️ Остались только: ингредиенты и суперпользователи"

docker-load-test-recipes:
	@echo "🍽️ Загрузка 12 тестовых рецептов..."
	cd infra && docker compose exec backend python create_test_recipes.py
	@echo "✅ Тестовые рецепты загружены!"

docker-reset-all-data: docker-clear-all-data docker-load-test-recipes
	@echo "🔄 Полный сброс данных с загрузкой тестовых рецептов завершен!"

docker-logs:
	@echo "📋 Просмотр логов Docker..."
	cd infra && docker compose logs -f

# === Docker Hub команды ===

docker-login:
	@echo "🔑 Авторизация в Docker Hub..."
	@echo "👤 Введите username: gdv001"
	@echo "🔐 Введите Personal Access Token"
	docker login -u gdv001

docker-push:
	@echo "📤 Пуш образов в Docker Hub..."
	./scripts/docker_push.sh

docker-push-version:
	@echo "📤 Пуш образов с версией в Docker Hub..."
	@read -p "Введите версию (например, v1.0.0): " version; \
	./scripts/docker_push.sh $$version

docker-publish: docker-build docker-push
	@echo "🚀 Полная публикация в Docker Hub завершена!"

# === Команды для production развертывания из Docker Hub ===

production-deploy: create-env
	@echo "🚀 Развертывание production из Docker Hub..."
	@if [ ! -f "infra/.env" ]; then echo "❌ Создайте infra/.env файл: make create-env"; exit 1; fi
	cd infra && docker compose -f docker-compose.production.yml up -d
	@echo "⏳ Ждем запуска контейнеров..."
	@sleep 15
	@echo "📊 Применяем миграции..."
	cd infra && docker compose -f docker-compose.production.yml exec backend python manage.py migrate || true
	@echo "📦 Загружаем данные..."
	cd infra && docker compose -f docker-compose.production.yml exec backend python manage.py loaddata fixtures/dev/ingredients_fixture.json || true
	cd infra && docker compose -f docker-compose.production.yml exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')" || true
	@echo ""
	@echo "🎉 Production развертывание завершено!"
	@echo "🌐 Приложение: http://localhost/"
	@echo "📖 API docs: http://localhost/api/docs/"
	@echo "🔧 Админка: http://localhost/admin/ (admin/admin)"
	@echo ""

production-down:
	@echo "🛑 Остановка production контейнеров..."
	cd infra && docker compose -f docker-compose.production.yml down

production-logs:
	@echo "📋 Логи production контейнеров..."
	cd infra && docker compose -f docker-compose.production.yml logs -f

production-restart:
	@echo "🔄 Перезапуск production..."
	cd infra && docker compose -f docker-compose.production.yml down
	cd infra && docker compose -f docker-compose.production.yml up -d
	@echo "⏳ Ждем запуска контейнеров..."
	@sleep 15
	@echo "📊 Применяем миграции..."
	cd infra && docker compose -f docker-compose.production.yml exec backend python manage.py migrate || true
	@echo "✅ Production перезапущен!"

# === Очистка тестовых данных (локальный сервер) ===

clear-test-users:
	@echo "🧪 Очистка тестовых пользователей Newman (локальный сервер)..."
	@cd backend && .venv/bin/python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); usernames_list = ['vasya.ivanov', 'second-user', 'third-user-username', 'NoEmail', 'NoFirstName', 'NoLastName', 'NoPassword', 'TooLongEmail', 'the-username-that-is-150-characters-long-and-should-not-pass-validation-if-the-serializer-is-configured-correctly-otherwise-the-current-test-will-fail-', 'TooLongFirstName', 'TooLongLastName', 'InvalidU\$$ername', 'EmailInUse']; deleted_count, _ = User.objects.filter(username__in=usernames_list).delete(); print(f'✅ Удалено {deleted_count} тестовых пользователей')"
