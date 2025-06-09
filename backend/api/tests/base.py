"""
Базовые классы для тестирования API.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class BaseAPITestCase:
    """
    Базовый класс для тестов API с общими методами.
    Используется для наследования в конкретных тестах API.
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, api_client, user, admin_user):
        """Инициализация перед каждым тестом."""
        self.client = api_client
        self.user = user
        self.admin_user = admin_user
        self.unauthorized_client = APIClient()

    def check_object_fields(self, obj_data, expected_fields):
        """Проверка наличия всех необходимых полей в данных объекта."""
        for field in expected_fields:
            assert field in obj_data, f"Поле {field} отсутствует в данных объекта"

    def check_status_code_and_data(self, response, expected_status, expected_fields=None):
        """
        Проверка статус-кода и данных ответа.

        Args:
            response: ответ API
            expected_status: ожидаемый HTTP-статус
            expected_fields: список полей, которые должны быть в ответе
        """
        assert response.status_code == expected_status, (
            f"Ожидался статус {expected_status}, получен {response.status_code}. "
            f"Ответ: {response.data if hasattr(response, 'data') else response.content}"
        )

        if expected_fields and hasattr(response, 'data'):
            if isinstance(response.data, list):
                if response.data:  # если список не пустой
                    self.check_object_fields(response.data[0], expected_fields)
            elif isinstance(response.data, dict):
                self.check_object_fields(response.data, expected_fields)


class BaseRecipeAPITest(BaseAPITestCase):
    """Базовый класс для тестов API рецептов."""

    @pytest.fixture(autouse=True)
    def setup_recipe_data(self, small_gif):
        """Подготовка данных для тестов рецептов."""
        from recipes.models import Ingredient

        # Создаем ингредиенты
        self.ingredient1 = Ingredient.objects.create(
            name='Яйцо', measurement_unit='шт'
        )
        self.ingredient2 = Ingredient.objects.create(
            name='Масло', measurement_unit='г'
        )

        # Подготовка тестовых данных рецепта
        self.recipe_data = {
            'name': 'Тестовый рецепт',
            'text': 'Описание тестового рецепта',
            'cooking_time': 15,
            'ingredients': [
                {'id': self.ingredient1.id, 'amount': 2},
                {'id': self.ingredient2.id, 'amount': 30}
            ],
            'image': small_gif
        }


class BaseUserAPITest(BaseAPITestCase):
    """Базовый класс для тестов API пользователей."""

    @pytest.fixture(autouse=True)
    def setup_user_data(self):
        """Подготовка данных для тестов пользователей."""
        self.new_user_data = {
            'username': 'newtestuser',
            'email': 'newtest@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword123'
        }
