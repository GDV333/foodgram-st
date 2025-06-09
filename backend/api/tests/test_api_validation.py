"""
Тесты для валидации данных и граничных случаев API.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status


User = get_user_model()


@pytest.mark.django_db
class TestAPIValidation:
    """Тесты для валидации данных в API."""

    def test_recipe_create_invalid_data(self, authenticated_client):
        """Тест создания рецепта с некорректными данными."""
        invalid_data = {
            'name': '',  # Пустое имя
            'text': '',  # Пустое описание
            'cooking_time': -1,  # Отрицательное время
            'ingredients': []  # Пустой список ингредиентов
        }

        response = authenticated_client.post(
            '/api/recipes/',
            invalid_data,
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_recipe_create_missing_fields(self, authenticated_client):
        """Тест создания рецепта без обязательных полей."""
        data = {'name': 'Test Recipe'}  # Только имя, остальные поля отсутствуют

        response = authenticated_client.post(
            '/api/recipes/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_registration_duplicate_email(self, api_client):
        """Тест регистрации пользователя с уже существующим email."""
        # Создаем пользователя
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='password123'
        )

        # Пытаемся создать пользователя с тем же email
        data = {
            'username': 'newuser',
            'email': 'test@example.com',  # Дублирующий email
            'password': 'password123'
        }

        response = api_client.post('/api/auth/users/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_subscription_self(self, authenticated_client, user):
        """Тест подписки на самого себя."""
        response = authenticated_client.post(f'/api/users/{user.id}/subscribe/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
