# Скрипты тестирования

Этот каталог содержит скрипты для запуска различных типов тестов проекта Foodgram.

## Доступные скрипты

### `run_pytest.py`
Запускает unit тесты Django с помощью pytest:
- Настраивает окружение для тестов
- Поддерживает покрытие кода
- Может тестировать отдельные приложения
- Генерирует HTML отчет о покрытии

**Использование:**
```bash
# Запуск всех тестов
./scripts/tests/run_pytest.py

# Запуск с подробным выводом
./scripts/tests/run_pytest.py --verbose

# Запуск с покрытием кода
./scripts/tests/run_pytest.py --coverage

# Тестирование конкретного приложения
./scripts/tests/run_pytest.py --app api

# Остановка после первой ошибки
./scripts/tests/run_pytest.py --failfast
```

### `run_newman.sh`
Запускает API тесты с помощью Newman (Postman CLI):
- Автоматически определяет, где запущен API (Docker или локальный сервер)
- Создает соответствующие переменные окружения
- Запускает коллекцию Postman тестов
- Автоматически очищает тестовых пользователей после завершения
- Генерирует JUnit XML отчет

**Использование:**
```bash
# Вариант 1: С Docker контейнерами
cd infra && docker-compose up -d
./scripts/tests/run_newman.sh

# Вариант 2: С локальным сервером
./scripts/dev/start_server.sh
# В другом терминале:
./scripts/tests/run_newman.sh
```


## Требования

### Для pytest тестов:
- Python 3.8+
- Установленные зависимости из requirements.txt
- pytest и связанные пакеты

### Для Newman тестов:
- Node.js и npm
- Newman: `npm install -g newman`
- Запущенный API сервер:
  - **Docker**: `cd infra && docker compose up -d` (http://localhost/api/)
  - **Локальный**: `./scripts/dev/start_server.sh` (http://localhost:8000/api/)

## Отчеты

### pytest
- HTML отчет о покрытии: `backend/htmlcov/index.html`
- Вывод в терминал с метриками покрытия

### Newman
- JUnit XML отчет: `postman_collection/newman-results.xml`
- Подробный вывод в терминал

## Быстрый запуск всех тестов

### С Docker контейнерами:
```bash
# 1. Запустите Docker контейнеры
cd infra && docker-compose up -d

# 2. В другом терминале запустите unit тесты
./scripts/tests/run_pytest.py --coverage

# 3. Запустите API тесты
./scripts/tests/run_newman.sh
```

### С локальным сервером:
```bash
# 1. Запустите Django сервер
./scripts/dev/start_server.sh

# 2. В другом терминале запустите unit тесты
./scripts/tests/run_pytest.py --coverage

# 3. Запустите API тесты
./scripts/tests/run_newman.sh

# 4. При необходимости очистите тестовых пользователей вручную
make clear-test-users
```

## Отладка тестов

### Если pytest тесты падают:
1. Проверьте, что все миграции применены
2. Убедитесь, что тестовая база данных чистая
3. Проверьте логи Django в `backend/django_logs.txt`

### Если Newman тесты падают:
1. Убедитесь, что Django сервер запущен и доступен
2. Проверьте, что тестовые данные созданы корректно
3. Проверьте логи сервера на наличие ошибок API
