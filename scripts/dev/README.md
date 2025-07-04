# Скрипты разработки

Этот каталог содержит скрипты для локальной разработки проекта Foodgram.

## Доступные скрипты

### `install_deps.sh`
Устанавливает все зависимости проекта:
- Создает виртуальное окружение Python
- Устанавливает зависимости Python из requirements.txt
- Устанавливает Newman для API тестов (если доступен npm)

**Использование:**
```bash
./scripts/dev/install_deps.sh
```

### `reset_db.sh`
Полностью сбрасывает базу данных и создает тестовые данные:
- Удаляет текущую базу данных
- Очищает миграции
- Создает новые миграции
- Применяет миграции
- Загружает базовые данные (ингредиенты)
- Создает тестовых пользователей и рецепты
- Предлагает создать суперпользователя

**Использование:**
```bash
./scripts/dev/reset_db.sh
```

### `start_server.sh`
Запускает Django сервер разработки:
- Активирует виртуальное окружение
- Устанавливает/обновляет зависимости
- Применяет миграции
- Загружает базовые данные
- Запускает сервер на http://localhost:8000

**Использование:**
```bash
./scripts/dev/start_server.sh
```

## Быстрый старт

1. Установите зависимости:
   ```bash
   ./scripts/dev/install_deps.sh
   ```

2. Подготовьте базу данных:
   ```bash
   ./scripts/dev/reset_db.sh
   ```

3. Запустите сервер:
   ```bash
   ./scripts/dev/start_server.sh
   ```

После этого API будет доступно по адресу http://localhost:8000/api/

## Тестовые пользователи

После выполнения `reset_db.sh` будут созданы следующие пользователи:
- `vasya.ivanov` (пароль: `testpass123`)
- `second-user` (пароль: `testpass123`)
- `third-user-username` (пароль: `testpass123`)
- `admin` (суперпользователь, пароль устанавливается интерактивно)
