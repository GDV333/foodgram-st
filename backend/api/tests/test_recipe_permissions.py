"""
Тесты для проверки прав доступа к рецептам.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status


User = get_user_model()


@pytest.mark.django_db
class TestRecipePermissions:
    """Тесты для проверки прав доступа к рецептам."""

    def test_retrieve_recipe_not_found(self, api_client):
        """Тест получения несуществующего рецепта."""
        response = api_client.get('/api/recipes/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_recipe_by_different_user(self, authenticated_client, recipe, ingredient):
        """Тест попытки обновления рецепта другим пользователем."""
        # Создаем другого пользователя
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='password'
        )
        authenticated_client.force_authenticate(user=other_user)

        data = {
            'name': 'Updated Recipe',
            'text': 'Updated description',
            'cooking_time': 45,
            'ingredients': [{'id': ingredient.id, 'amount': 150}]
        }

        response = authenticated_client.patch(
            f'/api/recipes/{recipe.id}/',
            data,
            format='json'
        )
        # Должен вернуть 403 Forbidden для чужого рецепта
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_recipe_by_different_user(self, authenticated_client, recipe):
        """Тест попытки удаления рецепта другим пользователем."""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='password'
        )
        authenticated_client.force_authenticate(user=other_user)

        response = authenticated_client.delete(f'/api/recipes/{recipe.id}/')
        # Должен вернуть 403 Forbidden для чужого рецепта
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_favorite_invalid_recipe_id(self, authenticated_client):
        """Тест добавления в избранное с некорректным ID рецепта."""
        response = authenticated_client.post('/api/recipes/invalid/favorite/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_favorite_recipe_not_found(self, authenticated_client):
        """Тест добавления в избранное несуществующего рецепта."""
        response = authenticated_client.post('/api/recipes/99999/favorite/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
