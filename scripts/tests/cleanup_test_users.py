#!/usr/bin/env python3
"""
Скрипт для очистки тестовых пользователей после Newman тестов.
Удаляет пользователей, созданных в процессе тестирования API.
"""

import os
import sys
import django

# Определяем пути
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..', '..')
backend_dir = os.path.join(project_root, 'backend')

# Переходим в директорию backend
os.chdir(backend_dir)

# Добавляем backend в sys.path
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

try:
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()
except Exception as e:
    print(f"❌ Ошибка настройки Django: {e}")
    print("📝 Убедитесь, что:")
    print("   - Django сервер запущен")
    print("   - База данных создана и мигрирована")
    print("   - Виртуальное окружение активировано")
    sys.exit(1)

# Тестовые пользователи из Newman коллекции
# Основные тестовые пользователи
TEST_USERNAMES = [
    'vasya.ivanov',
    'second-user', 
    'third-user-username'
]

# Дополнительные тестовые пользователи для проверки валидации
VALIDATION_TEST_USERNAMES = [
    'NoEmail',
    'NoFirstName', 
    'NoLastName',
    'NoPassword',
    'TooLongEmail',
    'the-username-that-is-150-characters-long-and-should-not-pass-validation-if-the-serializer-is-configured-correctly-otherwise-the-current-test-will-fail-',
    'TooLongFirstName',
    'TooLongLastName',
    'InvalidU$ername',
    'EmailInUse'
]

# Все тестовые пользователи
ALL_TEST_USERNAMES = TEST_USERNAMES + VALIDATION_TEST_USERNAMES

TEST_EMAILS = [
    'vivanov@yandex.ru',
    'second_user@email.org',
    'third-user@user.ru'
]

# Дополнительные тестовые email'ы для проверки валидации
VALIDATION_TEST_EMAILS = [
    'no-username@user.ru',
    'no-first-name@user.ru',
    'no-last-name@user.ru',
    'no-pasword@user.ru',
    'too-long-email@user.ru',
    'too-long-username@user.ru',
    'too-long-firt-name@user.ru',
    'too-long-last-name@user.ru',
    'invalid-username@user.ru',
    'username-in-use@user.ru'
]

# Все тестовые email'ы
ALL_TEST_EMAILS = TEST_EMAILS + VALIDATION_TEST_EMAILS

def cleanup_test_users():
    """Удаляет тестовых пользователей."""
    deleted_count = 0
    
    print("🧹 Начинаем очистку тестовых пользователей...")
    
    # Удаляем всех тестовых пользователей по username
    for username in ALL_TEST_USERNAMES:
        try:
            user = User.objects.get(username=username)
            user_id = user.id
            user.delete()
            print(f"✅ Удален пользователь {username} (ID: {user_id})")
            deleted_count += 1
        except User.DoesNotExist:
            print(f"ℹ️ Пользователь {username} не найден")
    
    # Дополнительно удаляем по email (на случай если username был изменен)
    for email in ALL_TEST_EMAILS:
        try:
            user = User.objects.get(email=email)
            # Проверяем, что этот пользователь еще не был удален
            if user.username not in ALL_TEST_USERNAMES:
                user_id = user.id
                username = user.username
                user.delete()
                print(f"✅ Удален пользователь {username} (email: {email}, ID: {user_id})")
                deleted_count += 1
        except User.DoesNotExist:
            continue
    
    # Удаляем пользователей с тестовыми именами (на случай ошибок в тестах)
    test_patterns = ['test', 'newman', 'api_test']
    for pattern in test_patterns:
        test_users = User.objects.filter(username__icontains=pattern)
        for user in test_users:
            if user.username not in ALL_TEST_USERNAMES:  # Избегаем двойного удаления
                user_id = user.id
                username = user.username
                user.delete()
                print(f"✅ Удален тестовый пользователь {username} (ID: {user_id})")
                deleted_count += 1
    
    if deleted_count > 0:
        print(f"🎉 Очистка завершена! Удалено пользователей: {deleted_count}")
    else:
        print("ℹ️ Тестовые пользователи не найдены или уже удалены")
    
    return deleted_count


if __name__ == '__main__':
    try:
        cleanup_test_users()
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        sys.exit(1)
