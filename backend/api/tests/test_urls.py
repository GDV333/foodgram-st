import pytest
from django.urls import reverse, resolve
from api.views import IngredientViewSet, RecipeViewSet


@pytest.mark.django_db
class TestURLConfiguration:
    """Тесты URL-маршрутизации."""

    def test_ingredient_list_url(self):
        """Тест URL для списка ингредиентов."""
        url = reverse('api:ingredient-list')
        assert url == '/api/ingredients/'
        resolver = resolve(url)
        assert resolver.func.cls == IngredientViewSet

    def test_ingredient_detail_url(self):
        """Тест URL для деталей ингредиента."""
        url = reverse('api:ingredient-detail', kwargs={'pk': 1})
        assert url == '/api/ingredients/1/'
        resolver = resolve(url)
        assert resolver.func.cls == IngredientViewSet

    def test_recipe_list_url(self):
        """Тест URL для списка рецептов."""
        url = reverse('api:recipe-list')
        assert url == '/api/recipes/'
        resolver = resolve(url)
        assert resolver.func.cls == RecipeViewSet

    def test_recipe_detail_url(self):
        """Тест URL для деталей рецепта."""
        url = reverse('api:recipe-detail', kwargs={'pk': 1})
        assert url == '/api/recipes/1/'
        resolver = resolve(url)
        assert resolver.func.cls == RecipeViewSet

    def test_recipe_favorite_url(self):
        """Тест URL для добавления в избранное."""
        url = reverse('api:recipe-favorite', kwargs={'pk': 1})
        assert url == '/api/recipes/1/favorite/'
        resolver = resolve(url)
        assert resolver.func.cls == RecipeViewSet

    def test_recipe_shopping_cart_url(self):
        """Тест URL для добавления в список покупок."""
        url = reverse('api:recipe-shopping-cart', kwargs={'pk': 1})
        assert url == '/api/recipes/1/shopping_cart/'
        resolver = resolve(url)
        assert resolver.func.cls == RecipeViewSet

    def test_recipe_download_shopping_cart_url(self):
        """Тест URL для скачивания списка покупок."""
        url = reverse('api:recipe-download-shopping-cart')
        assert url == '/api/recipes/download_shopping_cart/'
        resolver = resolve(url)
        assert resolver.func.cls == RecipeViewSet

    def test_user_list_url(self):
        """Тест URL для списка пользователей."""
        url = reverse('api:user-list')
        assert url == '/api/auth/users/'

    def test_user_me_url(self):
        """Тест URL для текущего пользователя."""
        url = reverse('api:user-me')
        assert url == '/api/auth/users/me/'

    def test_user_subscriptions_url(self):
        """Тест URL для подписок пользователя."""
        url = reverse('api:user-subscriptions')
        assert url == '/api/users/subscriptions/'
