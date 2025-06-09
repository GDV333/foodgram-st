import io
import pytest
from django.urls import reverse
from rest_framework import status
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from recipes.models import Recipe, Ingredient, RecipeIngredient, Favorite, ShoppingCart


@pytest.mark.django_db
class TestRecipeActions:
    """Тесты для действий с рецептами (favorite, shopping_cart, download_shopping_cart, get_link)."""

    @pytest.fixture
    def recipe_data(self, user):
        """Создает тестовый рецепт."""
        # Создаем ингредиент
        ingredient = Ingredient.objects.create(
            name='Тестовый ингредиент',
            measurement_unit='г'
        )

        # Создаем изображение для рецепта
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)

        image = SimpleUploadedFile(
            name='test_recipe.jpg',
            content=img_io.getvalue(),
            content_type='image/jpeg'
        )

        recipe = Recipe.objects.create(
            name='Тестовый рецепт',
            text='Описание тестового рецепта',
            cooking_time=30,
            author=user,
            image=image
        )

        # Добавляем ингредиент к рецепту
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=100
        )

        return recipe

    def test_favorite_add_success(self, authenticated_client, user, recipe_data):
        """Тест успешного добавления рецепта в избранное."""
        url = reverse('api:recipe-favorite', kwargs={'pk': recipe_data.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert 'name' in response.data
        assert 'cooking_time' in response.data
        assert Favorite.objects.filter(user=user, recipe=recipe_data).exists()

    def test_favorite_add_already_exists(self, authenticated_client, user, recipe_data):
        """Тест добавления рецепта в избранное, когда он уже там есть."""
        # Сначала добавляем в избранное
        Favorite.objects.create(user=user, recipe=recipe_data)

        url = reverse('api:recipe-favorite', kwargs={'pk': recipe_data.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data
        assert response.data['detail'] == 'Рецепт уже в избранном.'

    def test_favorite_delete_success(self, authenticated_client, user, recipe_data):
        """Тест успешного удаления рецепта из избранного."""
        # Сначала добавляем в избранное
        Favorite.objects.create(user=user, recipe=recipe_data)

        url = reverse('api:recipe-favorite', kwargs={'pk': recipe_data.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Favorite.objects.filter(user=user, recipe=recipe_data).exists()

    def test_favorite_delete_not_exists(self, authenticated_client, user, recipe_data):
        """Тест удаления рецепта из избранного, когда его там нет."""
        url = reverse('api:recipe-favorite', kwargs={'pk': recipe_data.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data
        assert response.data['detail'] == 'Рецепт не в избранном.'

    def test_favorite_invalid_recipe_id(self, authenticated_client):
        """Тест добавления в избранное с некорректным ID рецепта."""
        url = reverse('api:recipe-favorite', kwargs={'pk': 'invalid'})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data
        assert response.data['detail'] == 'Некорректный ID рецепта.'

    def test_favorite_nonexistent_recipe(self, authenticated_client):
        """Тест добавления в избранное несуществующего рецепта."""
        url = reverse('api:recipe-favorite', kwargs={'pk': 99999})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'detail' in response.data
        assert response.data['detail'] == 'Рецепт не найден.'

    def test_shopping_cart_add_success(self, authenticated_client, user, recipe_data):
        """Тест успешного добавления рецепта в корзину покупок."""
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': recipe_data.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert 'name' in response.data
        assert 'cooking_time' in response.data
        assert ShoppingCart.objects.filter(user=user, recipe=recipe_data).exists()

    def test_shopping_cart_add_already_exists(self, authenticated_client, user, recipe_data):
        """Тест добавления рецепта в корзину, когда он уже там есть."""
        # Сначала добавляем в корзину
        ShoppingCart.objects.create(user=user, recipe=recipe_data)

        url = reverse('api:recipe-shopping-cart', kwargs={'pk': recipe_data.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data
        assert response.data['detail'] == 'Рецепт уже в списке покупок.'

    def test_shopping_cart_delete_success(self, authenticated_client, user, recipe_data):
        """Тест успешного удаления рецепта из корзины покупок."""
        # Сначала добавляем в корзину
        ShoppingCart.objects.create(user=user, recipe=recipe_data)

        url = reverse('api:recipe-shopping-cart', kwargs={'pk': recipe_data.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ShoppingCart.objects.filter(user=user, recipe=recipe_data).exists()

    def test_shopping_cart_delete_not_exists(self, authenticated_client, user, recipe_data):
        """Тест удаления рецепта из корзины, когда его там нет."""
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': recipe_data.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data
        assert response.data['detail'] == 'Рецепт не в списке покупок.'

    def test_shopping_cart_invalid_recipe_id(self, authenticated_client):
        """Тест добавления в корзину с некорректным ID рецепта."""
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': 'invalid'})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data
        assert response.data['detail'] == 'Некорректный ID рецепта.'

    def test_shopping_cart_nonexistent_recipe(self, authenticated_client):
        """Тест добавления в корзину несуществующего рецепта."""
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': 99999})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'detail' in response.data
        assert response.data['detail'] == 'Рецепт не найден или не в списке покупок.'

    def test_download_shopping_cart_success(self, authenticated_client, user, recipe_data):
        """Тест успешного скачивания списка покупок."""
        # Добавляем рецепт в корзину покупок
        ShoppingCart.objects.create(user=user, recipe=recipe_data)

        url = reverse('api:recipe-download-shopping-cart')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/plain; charset=utf-8'
        assert 'Content-Disposition' in response
        assert 'attachment; filename="shopping_list.txt"' in response['Content-Disposition']
        assert 'Список покупок:' in response.content.decode('utf-8')
        assert 'Тестовый ингредиент' in response.content.decode('utf-8')

    def test_download_shopping_cart_empty(self, authenticated_client):
        """Тест скачивания пустого списка покупок."""
        url = reverse('api:recipe-download-shopping-cart')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert response.data['errors'] == 'В списке покупок нет рецептов'

    def test_get_link_success(self, api_client, recipe_data):
        """Тест успешного получения короткой ссылки на рецепт."""
        url = reverse('api:recipe-get-link', kwargs={'pk': recipe_data.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'short-link' in response.data
        assert f'/recipes/{recipe_data.id}/' in response.data['short-link']

    def test_get_link_invalid_recipe_id(self, api_client):
        """Тест получения ссылки с некорректным ID рецепта."""
        url = reverse('api:recipe-get-link', kwargs={'pk': 'invalid'})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data
        assert response.data['detail'] == 'Некорректный ID рецепта.'

    def test_get_link_nonexistent_recipe(self, api_client):
        """Тест получения ссылки для несуществующего рецепта."""
        url = reverse('api:recipe-get-link', kwargs={'pk': 99999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'detail' in response.data
        assert response.data['detail'] == 'Рецепт не найден.'

    def test_favorite_unauthenticated(self, api_client, recipe_data):
        """Тест попытки добавления в избранное неаутентифицированным пользователем."""
        url = reverse('api:recipe-favorite', kwargs={'pk': recipe_data.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_shopping_cart_unauthenticated(self, api_client, recipe_data):
        """Тест попытки добавления в корзину неаутентифицированным пользователем."""
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': recipe_data.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_download_shopping_cart_unauthenticated(self, api_client):
        """Тест попытки скачивания списка покупок неаутентифицированным пользователем."""
        url = reverse('api:recipe-download-shopping-cart')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
