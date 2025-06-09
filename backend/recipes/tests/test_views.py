import pytest
from django.urls import reverse
from rest_framework import status
from recipes.models import Recipe, Ingredient, RecipeIngredient, Favorite, ShoppingCart


@pytest.mark.django_db
class TestRecipeAPI:
    """Тесты для API рецептов."""

    @pytest.fixture
    def recipe_data(self, user, small_gif):
        """Фикстура для создания данных рецепта."""
        # Создаем ингредиенты
        ingredient1 = Ingredient.objects.create(name='Яйцо', measurement_unit='шт')
        ingredient2 = Ingredient.objects.create(name='Масло', measurement_unit='г')

        # Возвращаем данные для создания рецепта
        return {
            'name': 'Омлет',
            'text': 'Инструкция по приготовлению омлета',
            'cooking_time': 10,
            'author': user,
            'ingredients': [
                {'id': ingredient1.id, 'amount': 3},
                {'id': ingredient2.id, 'amount': 20}
            ],
            'image': small_gif
        }

    def test_recipe_list(self, authenticated_client, recipe_data):
        """Тест получения списка рецептов."""
        # Создаем рецепт для тестирования
        recipe = Recipe.objects.create(
            name=recipe_data['name'],
            text=recipe_data['text'],
            cooking_time=recipe_data['cooking_time'],
            author=recipe_data['author'],
            image=recipe_data['image']
        )

        for ingredient_data in recipe_data['ingredients']:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

        url = reverse('api:recipe-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_recipe_detail(self, authenticated_client, recipe_data):
        """Тест получения детальной информации о рецепте."""
        # Создаем рецепт для тестирования
        recipe = Recipe.objects.create(
            name=recipe_data['name'],
            text=recipe_data['text'],
            cooking_time=recipe_data['cooking_time'],
            author=recipe_data['author'],
            image=recipe_data['image']
        )

        for ingredient_data in recipe_data['ingredients']:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

        url = reverse('api:recipe-detail', kwargs={'pk': recipe.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == recipe_data['name']
        assert response.data['cooking_time'] == recipe_data['cooking_time']
        assert len(response.data['ingredients']) == 2
        assert 'measurement_unit' in response.data['ingredients'][0]

    def test_recipe_create(self, authenticated_client, recipe_data, small_gif):
        """Тест создания рецепта."""
        url = reverse('api:recipe-list')

        # Подготавливаем данные для запроса
        data = {
            'name': recipe_data['name'],
            'text': recipe_data['text'],
            'cooking_time': recipe_data['cooking_time'],
            'ingredients': [
                {'id': ing['id'], 'amount': ing['amount']}
                for ing in recipe_data['ingredients']
            ],
            'image': 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Recipe.objects.count() == 1
        assert Recipe.objects.first().name == recipe_data['name']

    def test_recipe_favorite(self, authenticated_client, user, recipe_data):
        """Тест добавления рецепта в избранное."""
        # Создаем рецепт
        recipe = Recipe.objects.create(
            name=recipe_data['name'],
            text=recipe_data['text'],
            cooking_time=recipe_data['cooking_time'],
            author=recipe_data['author'],
            image=recipe_data['image']
        )

        url = reverse('api:recipe-favorite', kwargs={'pk': recipe.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert Favorite.objects.filter(user=user, recipe=recipe).exists()

        # Тест удаления из избранного
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Favorite.objects.filter(user=user, recipe=recipe).exists()

    def test_recipe_shopping_cart(self, authenticated_client, user, recipe_data):
        """Тест добавления рецепта в список покупок."""
        # Создаем рецепт
        recipe = Recipe.objects.create(
            name=recipe_data['name'],
            text=recipe_data['text'],
            cooking_time=recipe_data['cooking_time'],
            author=recipe_data['author'],
            image=recipe_data['image']
        )

        url = reverse('api:recipe-shopping-cart', kwargs={'pk': recipe.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

        # Тест удаления из списка покупок
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

    def test_recipe_shopping_cart_download(self, authenticated_client, user, recipe_data):
        """Тест скачивания списка покупок."""
        # Создаем рецепт
        recipe = Recipe.objects.create(
            name=recipe_data['name'],
            text=recipe_data['text'],
            cooking_time=recipe_data['cooking_time'],
            author=recipe_data['author'],
            image=recipe_data['image']
        )

        # Добавляем ингредиенты в рецепт
        for ingredient_data in recipe_data['ingredients']:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

        # Добавляем рецепт в список покупок
        ShoppingCart.objects.create(user=user, recipe=recipe)

        url = reverse('api:recipe-download-shopping-cart')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/plain; charset=utf-8'
        assert 'attachment' in response['Content-Disposition']
