"""
Финальные тесты для достижения 90%+ покрытия кода.
Нацелены на реальные сценарии без неправильного мокирования.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from unittest.mock import patch

from recipes.models import Ingredient


User = get_user_model()


@pytest.mark.django_db
class TestViewsCoverageFinal:
    """Финальные тесты для достижения максимального покрытия."""

    def test_recipe_invalid_id_scenarios(self, api_client):
        """Тест различных невалидных ID рецептов."""
        # Тест с буквами в ID
        response = api_client.get('/api/recipes/abc/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Тест для favorite с невалидным ID
        response = api_client.post('/api/recipes/invalid/favorite/')
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

        # Тест для shopping_cart с невалидным ID
        response = api_client.post('/api/recipes/xyz/shopping_cart/')
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

        # Тест для get-link с невалидным ID
        response = api_client.get('/api/recipes/not_number/get-link/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_invalid_id_scenarios(self, api_client):
        """Тест различных невалидных ID пользователей."""
        # Тест с буквами в ID
        response = api_client.get('/api/users/abc/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Некорректный ID пользователя' in response.data['detail']

        # Тест с очень большим числом
        response = api_client.get('/api/users/999999999999999999999999999999999999999/')
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_recipe_exception_handlers(self, authenticated_client, recipe):
        """Тест обработки исключений в методах рецептов."""
        authenticated_client.force_authenticate(user=recipe.author)

        # Тест исключения в retrieve
        with patch('api.views.RecipeViewSet.get_object', side_effect=Exception("Test error")):
            response = authenticated_client.get(f'/api/recipes/{recipe.id}/')
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'Test error' in response.data['detail']

    def test_subscription_scenarios(self, authenticated_client, user):
        """Тест различных сценариев подписок."""
        # Создаем другого пользователя
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='password'
        )
        authenticated_client.force_authenticate(user=user)

        # Попытка подписаться на себя
        response = authenticated_client.post(f'/api/users/{user.id}/subscribe/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Нельзя подписаться на себя' in response.data['errors']

        # Подписка на пользователя
        response = authenticated_client.post(f'/api/users/{other_user.id}/subscribe/')
        assert response.status_code == status.HTTP_201_CREATED

        # Попытка повторной подписки
        response = authenticated_client.post(f'/api/users/{other_user.id}/subscribe/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Вы уже подписаны' in response.data['errors']

        # Отписка
        response = authenticated_client.delete(f'/api/users/{other_user.id}/subscribe/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Попытка отписки от несуществующей подписки
        response = authenticated_client.delete(f'/api/users/{other_user.id}/subscribe/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Вы не подписаны' in response.data['errors']

    def test_shopping_cart_scenarios(self, authenticated_client, recipe):
        """Тест различных сценариев списка покупок."""
        authenticated_client.force_authenticate(user=recipe.author)

        # Добавление в список покупок
        response = authenticated_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == status.HTTP_201_CREATED

        # Попытка повторного добавления
        response = authenticated_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'уже в списке покупок' in response.data['detail']

        # Удаление из списка покупок
        response = authenticated_client.delete(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Попытка удаления несуществующего элемента
        response = authenticated_client.delete(f'/api/recipes/{recipe.id}/shopping_cart/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'не в списке покупок' in response.data['detail']

    def test_favorite_scenarios(self, authenticated_client, recipe):
        """Тест различных сценариев избранного."""
        authenticated_client.force_authenticate(user=recipe.author)

        # Добавление в избранное
        response = authenticated_client.post(f'/api/recipes/{recipe.id}/favorite/')
        assert response.status_code == status.HTTP_201_CREATED

        # Попытка повторного добавления
        response = authenticated_client.post(f'/api/recipes/{recipe.id}/favorite/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'уже в избранном' in response.data['detail']

        # Удаление из избранного
        response = authenticated_client.delete(f'/api/recipes/{recipe.id}/favorite/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Попытка удаления несуществующего элемента
        response = authenticated_client.delete(f'/api/recipes/{recipe.id}/favorite/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'не в избранном' in response.data['detail']

    def test_download_shopping_cart_empty(self, authenticated_client, user):
        """Тест скачивания пустого списка покупок."""
        authenticated_client.force_authenticate(user=user)

        # Пустой список покупок
        response = authenticated_client.get('/api/recipes/download_shopping_cart/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'В списке покупок нет рецептов' in response.data['errors']

    def test_password_validation_scenarios(self, authenticated_client, user):
        """Тест различных сценариев валидации пароля."""
        authenticated_client.force_authenticate(user=user)

        # Отсутствие текущего пароля
        response = authenticated_client.post('/api/users/set_password/', {
            'new_password': 'newpassword123'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Необходимо указать текущий и новый пароль' in response.data['errors']

        # Отсутствие нового пароля
        response = authenticated_client.post('/api/users/set_password/', {
            'current_password': 'test'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Необходимо указать текущий и новый пароль' in response.data['errors']

        # Неверный текущий пароль
        response = authenticated_client.post('/api/users/set_password/', {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Неверный текущий пароль' in response.data['errors']

    def test_avatar_scenarios(self, authenticated_client, user):
        """Тест различных сценариев работы с аватаром."""
        authenticated_client.force_authenticate(user=user)

        # Установка валидного аватара
        avatar_data = {
            'avatar': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBggLDAsKDAkKCgr/2wBDAQICAgICAgUDAwUKBwYHCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgr/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA90IsA'
        }
        response = authenticated_client.put('/api/users/me/avatar/', avatar_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'avatar' in response.data

        # Удаление аватара
        response = authenticated_client.delete('/api/users/me/avatar/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_ingredient_search_filter_edge_cases(self, api_client):
        """Тест граничных случаев фильтра ингредиентов."""
        # Создаем ингредиенты для тестирования
        Ingredient.objects.create(name='Тестовый ингредиент', measurement_unit='г')

        # Поиск с пустым запросом
        response = api_client.get('/api/ingredients/', {'name': ''})
        assert response.status_code == status.HTTP_200_OK

        # Поиск с очень длинной строкой
        long_name = 'a' * 1000
        response = api_client.get('/api/ingredients/', {'name': long_name})
        assert response.status_code == status.HTTP_200_OK

        # Поиск с частичным совпадением
        response = api_client.get('/api/ingredients/', {'name': 'Тест'})
        assert response.status_code == status.HTTP_200_OK

    def test_nonexistent_recipe_actions(self, authenticated_client, user):
        """Тест действий с несуществующими рецептами."""
        authenticated_client.force_authenticate(user=user)

        # Несуществующий рецепт в favorite
        response = authenticated_client.post('/api/recipes/99999/favorite/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Несуществующий рецепт в shopping_cart
        response = authenticated_client.post('/api/recipes/99999/shopping_cart/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Несуществующий рецепт в get-link
        response = authenticated_client.get('/api/recipes/99999/get-link/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_subscription_invalid_user_id(self, authenticated_client, user):
        """Тест подписки с невалидным ID пользователя."""
        authenticated_client.force_authenticate(user=user)

        # Невалидный ID пользователя
        response = authenticated_client.post('/api/users/invalid/subscribe/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Некорректный ID пользователя' in response.data['errors']

        # Несуществующий пользователь
        response = authenticated_client.post('/api/users/99999/subscribe/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_recipe_permissions(self, api_client, authenticated_client, recipe):
        """Тест различных сценариев прав доступа."""
        # Неаутентифицированный пользователь может просматривать рецепты
        response = api_client.get(f'/api/recipes/{recipe.id}/')
        assert response.status_code == status.HTTP_200_OK

        # Неаутентифицированный пользователь может получать ссылки
        response = api_client.get(f'/api/recipes/{recipe.id}/get-link/')
        assert response.status_code == status.HTTP_200_OK

        # Проверяем различные комбинации для анонимных пользователей
        # Тест с несуществующим рецептом
        response = api_client.get('/api/recipes/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_avatar_invalid_data(self, authenticated_client, user):
        """Тест загрузки невалидных данных аватара."""
        authenticated_client.force_authenticate(user=user)

        # Невалидные данные аватара
        response = authenticated_client.put('/api/users/me/avatar/', {
            'avatar': 'invalid_base64_data'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Пустые данные
        response = authenticated_client.put('/api/users/me/avatar/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_edge_case_coverage(self, authenticated_client, user):
        """Тест дополнительных граничных случаев для покрытия."""
        authenticated_client.force_authenticate(user=user)

        # Тест subscriptions без подписок
        response = authenticated_client.get('/api/users/subscriptions/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

        # Тест me endpoint
        response = authenticated_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
