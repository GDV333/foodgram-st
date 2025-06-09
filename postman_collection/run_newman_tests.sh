#!/bin/bash
# Скрипт для запуска Newman тестов

# Убедитесь, что Newman установлен: npm install -g newman

# Переход в директорию с коллекцией Postman
cd "$(dirname "$0")"

# Очистка базы данных перед тестами
echo "Подготовка баз данных..."

# Очистка локальной SQLite базы (если существует)
if [ -f ../backend/db.sqlite3 ]; then
    echo "Подготовка локальной SQLite базы..."
    # Запуск clear_db.sh - он может вернуть ошибку, если пользователи не найдены
    # но это нормально для первого запуска
    bash ./clear_db.sh
    # Не проверяем код возврата, т.к. отсутствие пользователей - это нормально
    echo "Применение миграций и загрузка фикстур..."
    (cd ../backend && python manage.py migrate && python manage.py loaddata ../fixtures/dev/ingredients_fixture.json)
    if [ $? -ne 0 ]; then
        echo "Ошибка при миграции или загрузке фикстур. Тесты не будут запущены."
        exit 1
    fi
fi

# Очистка Docker базы (если доступна)
if command -v docker > /dev/null 2>&1; then
    echo "Очистка Docker базы данных перед тестами..."
    (cd ../infra && docker compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
usernames_list = ['vasya.ivanov', 'second-user', 'third-user-username', 'NoEmail', 'NoFirstName', 'NoLastName', 'NoPassword', 'TooLongEmail', 'the-username-that-is-150-characters-long-and-should-not-pass-validation-if-the-serializer-is-configured-correctly-otherwise-the-current-test-will-fail-', 'TooLongFirstName', 'TooLongLastName', 'InvalidU\$ername', 'EmailInUse']
deleted_count, _ = User.objects.filter(username__in=usernames_list).delete()
print(f'🧹 Удалено {deleted_count} тестовых пользователей из Docker перед тестами')
    ") 2>/dev/null || echo "⚠️  Docker контейнеры не запущены"
fi

# Запуск Newman тестов
# Предполагается, что сервер Django запущен на http://localhost:8000
# Если ваш сервер работает на другом URL или порту, измените его здесь
# Также можно передавать переменные окружения Postman через --env-var "host=http://localhost:8000"
echo "Запуск Newman тестов..."
newman run foodgram.postman_collection.json \
    --reporters cli,junit \
    --reporter-junit-export newman-results.xml

# Сохраняем код выхода Newman
NEWMAN_EXIT_CODE=$?

# Выполняем очистку тестовых данных после тестов
echo "Очистка тестовых данных после выполнения тестов..."

# Очистка локальной SQLite базы (если существует)
if [ -f ../backend/db.sqlite3 ]; then
    echo "Очистка локальной SQLite базы..."
    bash ./clear_db.sh
fi

# Очистка Docker базы (если доступна)
if command -v docker > /dev/null 2>&1; then
    echo "Попытка очистки Docker базы данных..."
    (cd ../infra && docker compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
usernames_list = ['vasya.ivanov', 'second-user', 'third-user-username', 'NoEmail', 'NoFirstName', 'NoLastName', 'NoPassword', 'TooLongEmail', 'the-username-that-is-150-characters-long-and-should-not-pass-validation-if-the-serializer-is-configured-correctly-otherwise-the-current-test-will-fail-', 'TooLongFirstName', 'TooLongLastName', 'InvalidU\$ername', 'EmailInUse']
deleted_count, _ = User.objects.filter(username__in=usernames_list).delete()
print(f'✅ Удалено {deleted_count} тестовых пользователей из Docker')
    ") 2>/dev/null || echo "⚠️  Docker контейнеры не запущены или очистка недоступна"
fi

echo "Очистка завершена."

# Опционально: остановить сервер Django, если он был запущен этим скриптом
# (требует доработки, если сервер запускается отдельно)

echo "Newman тесты завершены с кодом выхода: $NEWMAN_EXIT_CODE"
exit $NEWMAN_EXIT_CODE
