import pytest
from django.urls import reverse
from rest_framework import status
from recipes.models import Ingredient


@pytest.mark.django_db
class TestIngredientAPI:
    """Тесты для API ингредиентов."""

    def test_ingredient_list(self, authenticated_client):
        """Тест получения списка ингредиентов."""
        # Создаем тестовые ингредиенты
        Ingredient.objects.create(name='Соль', measurement_unit='г')
        Ingredient.objects.create(name='Сахар', measurement_unit='г')

        url = reverse('api:ingredient-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]['name'] == 'Сахар'  # Проверка сортировки по имени
        assert response.data[1]['name'] == 'Соль'
        assert 'measurement_unit' in response.data[0]

    def test_ingredient_detail(self, authenticated_client):
        """Тест получения деталей ингредиента."""
        ingredient = Ingredient.objects.create(
            name='Перец', measurement_unit='г'
        )

        url = reverse('api:ingredient-detail', kwargs={'pk': ingredient.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Перец'
        assert response.data['measurement_unit'] == 'г'

    def test_ingredient_search(self, authenticated_client):
        """Тест поиска ингредиентов."""
        Ingredient.objects.create(name='Соль', measurement_unit='г')
        Ingredient.objects.create(name='Сахар', measurement_unit='г')
        Ingredient.objects.create(name='Мука', measurement_unit='г')

        url = reverse('api:ingredient-list')
        response = authenticated_client.get(url, {'name': 'Са'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Сахар'
