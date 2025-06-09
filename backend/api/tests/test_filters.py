import pytest
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from api.filters import IngredientSearchFilter, RecipeFilter
from recipes.models import Recipe, Ingredient
from rest_framework.request import Request

User = get_user_model()


@pytest.mark.django_db
class TestIngredientSearchFilter:
    """Тесты для фильтра поиска ингредиентов."""

    def test_search_param(self):
        """Тест параметра поиска."""
        filter_instance = IngredientSearchFilter()
        assert filter_instance.search_param == 'name'


@pytest.mark.django_db
class TestRecipeFilter:
    """Тесты для фильтра рецептов."""

    def setup_method(self):
        """Настройка данных для тестов."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.author = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='testpass123',
            first_name='Author',
            last_name='User'
        )

        # Создаем ингредиенты
        self.ingredient1 = Ingredient.objects.create(
            name='Мука',
            measurement_unit='г'
        )
        self.ingredient2 = Ingredient.objects.create(
            name='Молоко',
            measurement_unit='мл'
        )

        # Создаем рецепт
        self.recipe = Recipe.objects.create(
            name='Тестовый рецепт',
            image='test_image.jpg',
            text='Описание рецепта',
            cooking_time=30,
            author=self.author
        )

    def test_filter_author_valid_id(self):
        """Тест фильтрации по автору с валидным ID."""
        request = self.factory.get('/', {'author': str(self.author.id)})
        request.user = self.user
        django_request = Request(request)

        filter_instance = RecipeFilter(
            request=django_request,
            queryset=Recipe.objects.all()
        )

        filtered_queryset = filter_instance.filter_author(
            Recipe.objects.all(), 'author', str(self.author.id)
        )

        assert self.recipe in filtered_queryset

    def test_filter_author_invalid_id(self):
        """Тест фильтрации по автору с невалидным ID."""
        request = self.factory.get('/', {'author': '{{userId}}'})
        request.user = self.user
        django_request = Request(request)

        filter_instance = RecipeFilter(
            request=django_request,
            queryset=Recipe.objects.all()
        )

        filtered_queryset = filter_instance.filter_author(
            Recipe.objects.all(), 'author', '{{userId}}'
        )

        assert not filtered_queryset.exists()

    def test_filter_author_empty_value(self):
        """Тест фильтрации по автору с пустым значением."""
        request = self.factory.get('/')
        request.user = self.user
        django_request = Request(request)

        filter_instance = RecipeFilter(
            request=django_request,
            queryset=Recipe.objects.all()
        )

        filtered_queryset = filter_instance.filter_author(
            Recipe.objects.all(), 'author', ''
        )

        assert self.recipe in filtered_queryset

    def test_filter_is_favorited_authenticated_user_true(self):
        """Тест фильтрации избранного для аутентифицированного пользователя."""
        # Добавляем рецепт в избранное
        from recipes.models import Favorite
        Favorite.objects.create(user=self.user, recipe=self.recipe)

        request = self.factory.get('/', {'is_favorited': 'true'})
        request.user = self.user
        django_request = Request(request)

        filter_instance = RecipeFilter(
            request=django_request,
            queryset=Recipe.objects.all()
        )

        filtered_queryset = filter_instance.filter_is_favorited(
            Recipe.objects.all(), 'is_favorited', True
        )

        assert self.recipe in filtered_queryset

    def test_filter_is_favorited_unauthenticated_user(self):
        """Тест фильтрации избранного для неаутентифицированного пользователя."""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get('/', {'is_favorited': 'true'})
        request.user = AnonymousUser()
        django_request = Request(request)

        filter_instance = RecipeFilter(
            request=django_request,
            queryset=Recipe.objects.all()
        )

        filtered_queryset = filter_instance.filter_is_favorited(
            Recipe.objects.all(), 'is_favorited', True
        )

        assert self.recipe in filtered_queryset

    def test_filter_is_favorited_false(self):
        """Тест фильтрации избранного с значением False."""
        request = self.factory.get('/')
        request.user = self.user
        django_request = Request(request)

        filter_instance = RecipeFilter(
            request=django_request,
            queryset=Recipe.objects.all()
        )

        filtered_queryset = filter_instance.filter_is_favorited(
            Recipe.objects.all(), 'is_favorited', False
        )

        assert self.recipe in filtered_queryset

    def test_filter_is_in_shopping_cart_authenticated_user_true(self):
        """Тест фильтрации корзины для аутентифицированного пользователя."""
        # Добавляем рецепт в корзину
        from recipes.models import ShoppingCart
        ShoppingCart.objects.create(user=self.user, recipe=self.recipe)

        request = self.factory.get('/', {'is_in_shopping_cart': 'true'})
        request.user = self.user
        django_request = Request(request)

        filter_instance = RecipeFilter(
            request=django_request,
            queryset=Recipe.objects.all()
        )

        filtered_queryset = filter_instance.filter_is_in_shopping_cart(
            Recipe.objects.all(), 'is_in_shopping_cart', True
        )

        assert self.recipe in filtered_queryset

    def test_filter_is_in_shopping_cart_unauthenticated_user(self):
        """Тест фильтрации корзины для неаутентифицированного пользователя."""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get('/', {'is_in_shopping_cart': 'true'})
        request.user = AnonymousUser()
        django_request = Request(request)

        filter_instance = RecipeFilter(
            request=django_request,
            queryset=Recipe.objects.all()
        )

        filtered_queryset = filter_instance.filter_is_in_shopping_cart(
            Recipe.objects.all(), 'is_in_shopping_cart', True
        )

        assert self.recipe in filtered_queryset

    def test_filter_is_in_shopping_cart_false(self):
        """Тест фильтрации корзины с значением False."""
        request = self.factory.get('/')
        request.user = self.user
        django_request = Request(request)

        filter_instance = RecipeFilter(
            request=django_request,
            queryset=Recipe.objects.all()
        )

        filtered_queryset = filter_instance.filter_is_in_shopping_cart(
            Recipe.objects.all(), 'is_in_shopping_cart', False
        )

        assert self.recipe in filtered_queryset
