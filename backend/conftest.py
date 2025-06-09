import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для создания клиента API."""
    return APIClient()


@pytest.fixture
def user():
    """Фикстура для создания обычного пользователя."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        password='testpassword'
    )


@pytest.fixture
def admin_user():
    """Фикстура для создания администратора."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        password='adminpassword'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Фикстура для создания аутентифицированного клиента."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Фикстура для создания клиента с правами администратора."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def small_gif():
    """Фикстура, создающая небольшой тестовый GIF-файл."""
    return SimpleUploadedFile(
        name='small.gif',
        content=(
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00'
            b'\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        ),
        content_type='image/gif'
    )


@pytest.fixture
def ingredient():
    """Фикстура для создания ингредиента."""
    from recipes.models import Ingredient
    return Ingredient.objects.create(
        name='Тестовый ингредиент',
        measurement_unit='г'
    )


@pytest.fixture
def recipe(user, ingredient):
    """Фикстура для создания рецепта."""
    from recipes.models import Recipe, RecipeIngredient
    recipe = Recipe.objects.create(
        name='Тестовый рецепт',
        text='Описание тестового рецепта',
        cooking_time=30,
        image='test_image.jpg',
        author=user
    )
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=100
    )
    return recipe


@pytest.fixture
def user_with_recipes(user, ingredient):
    """Фикстура для создания пользователя с несколькими рецептами."""
    from recipes.models import Recipe, RecipeIngredient

    # Создаем 3 рецепта для пользователя
    for i in range(1, 4):
        recipe = Recipe.objects.create(
            name=f'Рецепт {i}',
            text=f'Описание рецепта {i}',
            cooking_time=30 + i * 10,
            image=f'test_image_{i}.jpg',
            author=user
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=100 + i * 50
        )

    return user
