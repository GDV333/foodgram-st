# Настройка логирования в Django проекте Foodgram

## Обзор

В проекте настроена комплексная система логирования для отладки и мониторинга всех компонентов Django приложения.

## Структура логирования

### 1. Файлы конфигурации

- **`/backend/foodgram/logging_config.py`** - основная конфигурация логирования
- **`/backend/api/logging_middleware.py`** - middleware для логирования запросов и SQL

### 2. Файлы логов

Все логи сохраняются в директории `/backend/logs/`:

- **`django_debug.log`** - все отладочные сообщения и информация
- **`django_error.log`** - только ошибки и критические сообщения  
- **`django_sql.log`** - SQL запросы и их производительность

### 3. Форматы логов

#### Детальный формат (debug.log):
```
[2025-06-08 07:43:54] INFO api.middleware logging_middleware 3266058 126364892001984 /path/to/file.py:21 - Сообщение
```

#### Простой формат (error.log):
```
[2025-06-08 07:42:56] ERROR api.middleware logging_middleware /path/to/file.py:66 - Ошибка
```

#### SQL формат:
```
[2025-06-08 07:43:54] SQL: (0.000) SELECT "recipes_ingredient"."id", "recipes_ingredient"."name", "recipes_ingredient"."measurement_unit" FROM "recipes_ingredient" ORDER BY "recipes_ingredient"."name" ASC; args=(); alias=default
```

## Компоненты логирования

### 1. Логгеры по модулям

- **`django`** - базовые события Django
- **`api`** - события API слоя
- **`recipes`** - события модуля рецептов
- **`users`** - события модуля пользователей
- **`django.db.backends`** - SQL запросы
- **`rest_framework`** - события DRF

### 2. Middleware логирования

#### LoggingMiddleware
- Логирует все HTTP запросы и ответы
- Записывает IP адрес, User-Agent, время выполнения
- Обрабатывает ошибки и исключения
- Логирует GET/POST параметры

#### DatabaseQueryLoggingMiddleware  
- Отслеживает количество SQL запросов на каждый request
- Помогает выявлять N+1 проблемы

### 3. Ротация логов

- Файлы логов автоматически ротируются при достижении 10MB
- Сохраняется до 5 резервных копий каждого лога
- Старые файлы автоматически сжимаются

## Примеры использования

### В view:

```python
import logging

logger = logging.getLogger('api')

def my_view(request):
    logger.info(f"Обработка запроса от пользователя {request.user}")
    try:
        # ваш код
        logger.debug("Операция выполнена успешно")
    except Exception as e:
        logger.error(f"Ошибка в операции: {e}")
```

### В моделях:

```python
import logging

logger = logging.getLogger('recipes')

class Recipe(models.Model):
    def save(self, *args, **kwargs):
        logger.info(f"Сохранение рецепта: {self.name}")
        super().save(*args, **kwargs)
```

## Мониторинг логов

### Просмотр логов в реальном времени:

```bash
# Все отладочные сообщения
tail -f logs/django_debug.log

# Только ошибки
tail -f logs/django_error.log

# SQL запросы
tail -f logs/django_sql.log
```

### Фильтрация логов:

```bash
# Запросы к определенному endpoint
grep "/api/ingredients/" logs/django_debug.log

# Ошибки 500
grep "500" logs/django_debug.log

# SQL запросы с долгим выполнением
grep -E "SQL.*\([0-9]\.[0-9]{3,}" logs/django_sql.log
```

## Настройки по окружениям

### Development
- Логи выводятся как в файлы, так и в консоль
- Уровень логирования: DEBUG
- SQL запросы логируются подробно

### Production (рекомендации)
- Только файловое логирование
- Уровень логирования: INFO
- Отключить логирование SQL в production

## Производительность

- Файловые логи работают асинхронно
- Ротация предотвращает переполнение диска
- SQL логирование можно отключить для критических производственных нагрузок

## Устранение неполадок

### Проверка конфигурации:
```python
import logging
logging.getLogger('django').info("Тест логирования")
```

### Проверка файлов:
- Убедитесь, что директория `/backend/logs/` доступна для записи
- Проверьте права доступа к файлам логов

### Очистка логов:
```bash
# Очистка всех логов
rm logs/*.log

# Очистка только старых логов
find logs/ -name "*.log.*" -delete
```

## Полезные команды

### Анализ трафика:
```bash
# Топ запрашиваемых endpoints
grep "Запрос:" logs/django_debug.log | awk '{print $8}' | sort | uniq -c | sort -nr

# Медленные запросы (>100ms)
grep -E "за [0-9]\.[0-9]{3,}с" logs/django_debug.log

# Статистика по кодам ответов
grep "Ответ:" logs/django_debug.log | awk '{print $8}' | sort | uniq -c
```

### Мониторинг ошибок:
```bash
# Последние ошибки
tail -20 logs/django_error.log

# Количество ошибок по типам
grep -o "ERROR.*:" logs/django_error.log | sort | uniq -c
```
