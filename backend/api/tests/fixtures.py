"""
Фикстуры для тестов в формате JSON.
Используется для создания тестовых данных.
"""

import json

# Тестовые ингредиенты
INGREDIENTS_FIXTURE = [
    {"model": "recipes.ingredient", "pk": 1, "fields": {"name": "Соль", "measurement_unit": "г"}},
    {"model": "recipes.ingredient", "pk": 2, "fields": {"name": "Сахар", "measurement_unit": "г"}},
    {"model": "recipes.ingredient", "pk": 3, "fields": {"name": "Мука", "measurement_unit": "г"}},
    {"model": "recipes.ingredient", "pk": 4, "fields": {"name": "Масло сливочное", "measurement_unit": "г"}},
    {"model": "recipes.ingredient", "pk": 5, "fields": {"name": "Молоко", "measurement_unit": "мл"}},
    {"model": "recipes.ingredient", "pk": 6, "fields": {"name": "Яйцо", "measurement_unit": "шт"}}
]

# Тестовые пользователи
USERS_FIXTURE = [
    {
        "model": "users.user",
        "pk": 1,
        "fields": {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "pbkdf2_sha256$260000$3iGMyk4PFP2HxojII0eqIm$f+1JGcbkiNp3bYYE4LnQPM41nBSVE6zRiyaX3ec5Ucc=",  # testpassword
            "is_active": True
        }
    },
    {
        "model": "users.user",
        "pk": 2,
        "fields": {
            "username": "testadmin",
            "email": "testadmin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "password": "pbkdf2_sha256$260000$H0lrNUmA0KoABl8VY6NQJc$K6+2MJsBOZWetX3d5QANWl/TbH7njuTxP0Ksi5g3h2E=",  # adminpassword
            "is_active": True,
            "is_staff": True,
            "is_superuser": True
        }
    }
]


def get_fixtures(fixture_type=None):
    """
    Получить фикстуры заданного типа или все фикстуры.

    Args:
        fixture_type (str, optional): Тип фикстуры ('ingredients', 'users')

    Returns:
        list: Данные фикстуры в формате JSON
    """
    if fixture_type == 'ingredients':
        return INGREDIENTS_FIXTURE
    elif fixture_type == 'users':
        return USERS_FIXTURE
    else:
        # Возвращаем все фикстуры вместе
        return INGREDIENTS_FIXTURE + USERS_FIXTURE


def save_fixtures(fixture_type=None, filepath=None):
    """
    Сохранить фикстуры в JSON-файл.

    Args:
        fixture_type (str, optional): Тип фикстуры
        filepath (str, optional): Путь для сохранения файла
    """
    if not filepath:
        filepath = f"fixtures_{fixture_type}.json" if fixture_type else "fixtures_all.json"

    with open(filepath, 'w') as f:
        json.dump(get_fixtures(fixture_type), f, indent=4)
