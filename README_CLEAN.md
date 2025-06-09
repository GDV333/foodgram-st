# Фудграм - Recipe Sharing Platform

![Foodgram Logo](https://img.shields.io/badge/Foodgram-Recipe%20Sharing-orange)
![CI/CD](https://github.com/GDV333/foodgram-st/workflows/Foodgram%20CI/CD/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-enabled-blue)

Фудграм — веб-приложение для публикации и обмена рецептами. Пользователи могут публиковать свои рецепты, добавлять понравившиеся рецепты в избранное, подписываться на публикации других авторов и формировать список покупок для выбранных блюд.

## Функциональные возможности

### Неавторизованные пользователи
- Просмотр рецептов на главной странице
- Просмотр отдельных страниц рецептов
- Просмотр страниц пользователей
- Создание аккаунта

### Авторизованные пользователи
- Вход в систему под своим логином и паролем
- Выход из системы
- Создание, редактирование и удаление собственных рецептов
- Смена своего аватара
- Работа с персональным списком покупок: добавление и удаление любых рецептов, выгрузка файла с количеством необходимых ингредиентов
- Работа с персональным списком избранного: добавление в него рецептов или удаление их, просмотр своей страницы избранных рецептов
- Подписка на публикации авторов рецептов и отмена подписки, просмотр своей страницы подписок

### Администраторы
- Все права авторизованного пользователя
- Изменение пароля любого пользователя
- Создание, блокировка и удаление аккаунтов пользователей
- Редактирование и удаление любых рецептов

## Архитектура проекта

```
foodgram-st/
├── backend/           # Django REST API
├── frontend/          # React SPA приложение
├── infra/            # Docker Compose конфигурация
├── data/             # Данные для загрузки (ингредиенты)
├── docs/             # Документация API
├── postman_collection/ # Тесты API
├── fixtures/         # Фикстуры для разработки и тестов
└── scripts/          # Вспомогательные скрипты
```

## Технологический стек

### Backend
- **Python 3.12** - язык программирования
- **Django 5.0** - веб-фреймворк
- **Django REST Framework** - API фреймворк
- **Djoser** - аутентификация и управление пользователями
- **PostgreSQL** - основная база данных
- **SQLite** - база данных для разработки
- **Gunicorn** - WSGI сервер

### Frontend
- **React** - JavaScript фреймворк
- **Create React App** - инструмент сборки

### Инфраструктура
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация контейнеров
- **Nginx** - веб-сервер и прокси
- **GitHub Actions** - CI/CD

## Модели данных

### Рецепт
- Автор публикации (пользователь)
- Название
- Картинка
- Текстовое описание
- Ингредиенты с указанием количества и единицы измерения
- Время приготовления в минутах

### Ингредиент
- Название
- Единица измерения

### Дополнительные модели
- **User** - расширенная модель пользователя Django
- **Tag** - теги для категоризации рецептов
- **Favorite** - избранные рецепты пользователей
- **ShoppingCart** - списки покупок пользователей
- **Subscription** - подписки на авторов

## Системные требования

- Docker и Docker Compose
- Python 3.12+ (для локальной разработки)
- Node.js 18+ (для фронтенда)

## Быстрый старт

### Запуск в Docker (рекомендуется)

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/your-repo/foodgram-st.git
   cd foodgram-st
   ```

2. **Создайте .env файл:**
   ```bash
   make create-env
   ```

3. **Запустите проект одной командой:**
   ```bash
   make setup
   ```

4. **Откройте в браузере:**
   - Приложение: http://localhost
   - Документация API: http://localhost/api/docs/
   - Админ-панель: http://localhost/admin/

### Альтернативные команды

```bash
# Быстрый перезапуск (если уже настроено)
make quick-start

# Запуск в production режиме
make production

# Сброс и пересоздание данных
make dev-reset
```

## Пользователи по умолчанию

После настройки создаются тестовые пользователи:

### Администратор
- **Username:** admin
- **Email:** admin@foodgram.com
- **Password:** admin123

### Обычные пользователи
- **Username:** testuser
- **Email:** test@foodgram.com
- **Password:** testpass123

## Тестирование

### Все тесты
```bash
make test
```

### Unit тесты (pytest)
```bash
make test-unit
```

### API тесты (Newman/Postman)
```bash
make test-api
```

### Покрытие кода
```bash
make test-coverage
```

## API Документация

Интерактивная документация доступна по адресам:
- **ReDoc:** http://localhost/api/docs/
- **Swagger:** http://localhost/api/schema/swagger-ui/

### Основные endpoints

```
GET    /api/recipes/           - Список рецептов
POST   /api/recipes/           - Создать рецепт
GET    /api/recipes/{id}/      - Детали рецепта
GET    /api/ingredients/       - Список ингредиентов
GET    /api/tags/              - Список тегов
POST   /api/auth/token/login/  - Получить токен
POST   /api/auth/users/        - Регистрация
GET    /api/users/me/          - Профиль пользователя
```

## Разработка

### Настройка локального окружения

1. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

2. **Установите зависимости:**
   ```bash
   make install
   ```

3. **Настройте окружение разработки:**
   ```bash
   make dev-setup
   ```

4. **Запустите сервер разработки:**
   ```bash
   make dev-start
   ```

### Полезные команды

```bash
# Проверка кода
make lint              # Линтеры (flake8)
make format            # Форматирование (black, isort)
make check-all         # Все проверки

# Управление данными
make load-data         # Загрузить ингредиенты
make dev-reset         # Сбросить БД

# Docker команды
make docker-build      # Собрать образы
make docker-up         # Запустить контейнеры
make docker-down       # Остановить контейнеры
make docker-logs       # Просмотр логов

# Очистка
make clean             # Удалить временные файлы
```

## Структура проекта

### Backend (Django)

```
backend/
├── foodgram/          # Основные настройки Django
├── api/               # API endpoints и логика
├── recipes/           # Модели и логика рецептов
├── users/             # Модели и логика пользователей
├── requirements.txt   # Python зависимости
└── Dockerfile         # Docker образ
```

## Docker развертывание

### Локальная разработка

```bash
cd infra
docker compose up -d
```

### Production

```bash
cd infra
docker compose -f docker-compose.production.yml up -d
```

### Переменные окружения

Создайте файл `infra/.env`:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Docker Hub (опционально)
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-token
```

## Мониторинг и логирование

Проект включает систему логирования:

- **Debug логи:** `backend/logs/django_debug.log`
- **Ошибки:** `backend/logs/django_error.log`
- **SQL запросы:** `backend/logs/django_sql.log`

```bash
# Просмотр логов в реальном времени
tail -f backend/logs/django_debug.log

# В Docker
make docker-logs
```
