import base64
import io
import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from PIL import Image
from rest_framework.exceptions import ValidationError

from recipes.models import Favorite, ShoppingCart
from users.models import Subscription
from api.serializers import (
    Base64ImageField, CustomUserSerializer, RecipeWriteSerializer,
    RecipeReadSerializer, SubscriptionSerializer, FavoriteSerializer,
    ShoppingCartSerializer, SetAvatarSerializer,
    RecipeIngredientWriteSerializer
)


@pytest.mark.django_db
class TestBase64ImageField:
    """Тесты для Base64ImageField."""

    def test_base64_image_processing(self):
        """Тест обработки изображения в формате Base64."""
        # Создаем простое изображение
        img = Image.new('RGB', (10, 10), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)

        # Кодируем в Base64
        img_b64 = base64.b64encode(img_io.getvalue()).decode()
        data_uri = f'data:image/png;base64,{img_b64}'

        field = Base64ImageField()
        result = field.to_internal_value(data_uri)

        assert result is not None
        assert result.name.endswith('.png')

    def test_base64_image_jpeg_format(self):
        """Тест обработки JPEG изображения в формате Base64."""
        # Создаем JPEG изображение
        img = Image.new('RGB', (10, 10), color='blue')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)

        # Кодируем в Base64
        img_b64 = base64.b64encode(img_io.getvalue()).decode()
        data_uri = f'data:image/jpeg;base64,{img_b64}'

        field = Base64ImageField()
        result = field.to_internal_value(data_uri)

        assert result is not None
        assert result.name.endswith('.jpeg')


@pytest.mark.django_db
class TestCustomUserSerializer:
    """Тесты для CustomUserSerializer."""

    def test_is_subscribed_anonymous_user(self, user):
        """Тест поля is_subscribed для анонимного пользователя."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()

        serializer = CustomUserSerializer(user, context={'request': request})
        assert serializer.data['is_subscribed'] is False

    def test_is_subscribed_authenticated_subscribed(self, user, admin_user):
        """Тест поля is_subscribed для подписанного пользователя."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user

        # Создаем подписку
        Subscription.objects.create(user=user, author=admin_user)

        serializer = CustomUserSerializer(admin_user, context={'request': request})
        assert serializer.data['is_subscribed'] is True

    def test_is_subscribed_authenticated_not_subscribed(self, user, admin_user):
        """Тест поля is_subscribed для неподписанного пользователя."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user

        serializer = CustomUserSerializer(admin_user, context={'request': request})
        assert serializer.data['is_subscribed'] is False


@pytest.mark.django_db
class TestRecipeWriteSerializer:
    """Тесты для RecipeWriteSerializer."""

    def test_validate_ingredients_empty(self):
        """Тест валидации пустого списка ингредиентов."""
        serializer = RecipeWriteSerializer()

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_ingredients([])

        assert 'Нужно указать хотя бы один ингредиент.' in str(exc_info.value)

    def test_validate_ingredients_duplicates(self, ingredient):
        """Тест валидации дублирующихся ингредиентов."""
        serializer = RecipeWriteSerializer()
        ingredients_data = [
            {'id': ingredient, 'amount': 100},
            {'id': ingredient, 'amount': 200}
        ]

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_ingredients(ingredients_data)

        assert 'Ингредиенты не должны повторяться.' in str(exc_info.value)

    def test_validate_cooking_time_negative(self):
        """Тест валидации отрицательного времени приготовления."""
        serializer = RecipeWriteSerializer()

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_cooking_time(-1)

        assert 'Время приготовления должно быть больше 0.' in str(exc_info.value)

    def test_validate_cooking_time_zero(self):
        """Тест валидации нулевого времени приготовления."""
        serializer = RecipeWriteSerializer()

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_cooking_time(0)

        assert 'Время приготовления должно быть больше 0.' in str(exc_info.value)

    def test_update_without_ingredients(self, recipe):
        """Тест обновления рецепта без указания ингредиентов."""
        serializer = RecipeWriteSerializer()
        validated_data = {'name': 'Новое название'}

        with pytest.raises(ValidationError) as exc_info:
            serializer.update(recipe, validated_data)

        assert 'Это поле обязательно.' in str(exc_info.value)

    def test_update_recipe_success(self, recipe, ingredient):
        """Тест успешного обновления рецепта."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = recipe.author

        validated_data = {
            'name': 'Обновленное название',
            'text': 'Обновленное описание',
            'cooking_time': 45,
            'ingredients': [{'id': ingredient, 'amount': 150}]
        }

        serializer = RecipeWriteSerializer(context={'request': request})
        updated_recipe = serializer.update(recipe, validated_data)

        assert updated_recipe.name == 'Обновленное название'
        assert updated_recipe.text == 'Обновленное описание'
        assert updated_recipe.cooking_time == 45


@pytest.mark.django_db
class TestRecipeReadSerializer:
    """Тесты для RecipeReadSerializer."""

    def test_is_favorited_anonymous_user(self, recipe):
        """Тест поля is_favorited для анонимного пользователя."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()

        serializer = RecipeReadSerializer(recipe, context={'request': request})
        assert serializer.data['is_favorited'] is False

    def test_is_favorited_authenticated_favorited(self, recipe, user):
        """Тест поля is_favorited для рецепта в избранном."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user

        Favorite.objects.create(user=user, recipe=recipe)

        serializer = RecipeReadSerializer(recipe, context={'request': request})
        assert serializer.data['is_favorited'] is True

    def test_is_in_shopping_cart_anonymous_user(self, recipe):
        """Тест поля is_in_shopping_cart для анонимного пользователя."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()

        serializer = RecipeReadSerializer(recipe, context={'request': request})
        assert serializer.data['is_in_shopping_cart'] is False

    def test_is_in_shopping_cart_authenticated_in_cart(self, recipe, user):
        """Тест поля is_in_shopping_cart для рецепта в корзине."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user

        ShoppingCart.objects.create(user=user, recipe=recipe)

        serializer = RecipeReadSerializer(recipe, context={'request': request})
        assert serializer.data['is_in_shopping_cart'] is True


@pytest.mark.django_db
class TestSubscriptionSerializer:
    """Тесты для SubscriptionSerializer."""

    def test_get_is_subscribed_always_true(self, user):
        """Тест поля is_subscribed всегда возвращает True."""
        serializer = SubscriptionSerializer(user)
        assert serializer.data['is_subscribed'] is True

    def test_get_recipes_with_limit(self, user_with_recipes):
        """Тест получения рецептов с ограничением."""
        factory = RequestFactory()
        request = factory.get('/?recipes_limit=1')

        serializer = SubscriptionSerializer(user_with_recipes, context={'request': request})
        assert len(serializer.data['recipes']) == 1

    def test_get_recipes_invalid_limit(self, user_with_recipes):
        """Тест получения рецептов с некорректным ограничением."""
        factory = RequestFactory()
        request = factory.get('/?recipes_limit=invalid')

        serializer = SubscriptionSerializer(user_with_recipes, context={'request': request})
        # При некорректном лимите должны вернуться все рецепты
        assert len(serializer.data['recipes']) == user_with_recipes.recipes.count()

    def test_get_recipes_count(self, user_with_recipes):
        """Тест получения количества рецептов."""
        serializer = SubscriptionSerializer(user_with_recipes)
        assert serializer.data['recipes_count'] == user_with_recipes.recipes.count()


@pytest.mark.django_db
class TestFavoriteSerializer:
    """Тесты для FavoriteSerializer."""

    def test_validate_duplicate_favorite(self, user, recipe):
        """Тест валидации повторного добавления в избранное."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user

        # Создаем существующую запись в избранном
        Favorite.objects.create(user=user, recipe=recipe)

        serializer = FavoriteSerializer(context={'request': request})
        data = {'user': user, 'recipe': recipe}

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate(data)

        assert 'Рецепт уже в избранном.' in str(exc_info.value)

    def test_validate_new_favorite(self, user, recipe):
        """Тест валидации нового добавления в избранное."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user

        serializer = FavoriteSerializer(context={'request': request})
        data = {'user': user, 'recipe': recipe}

        validated_data = serializer.validate(data)
        assert validated_data == data


@pytest.mark.django_db
class TestShoppingCartSerializer:
    """Тесты для ShoppingCartSerializer."""

    def test_validate_duplicate_shopping_cart(self, user, recipe):
        """Тест валидации повторного добавления в корзину покупок."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user

        # Создаем существующую запись в корзине
        ShoppingCart.objects.create(user=user, recipe=recipe)

        serializer = ShoppingCartSerializer(context={'request': request})
        data = {'user': user, 'recipe': recipe}

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate(data)

        assert 'Рецепт уже в списке покупок.' in str(exc_info.value)

    def test_validate_new_shopping_cart(self, user, recipe):
        """Тест валидации нового добавления в корзину покупок."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user

        serializer = ShoppingCartSerializer(context={'request': request})
        data = {'user': user, 'recipe': recipe}

        validated_data = serializer.validate(data)
        assert validated_data == data


@pytest.mark.django_db
class TestSetAvatarSerializer:
    """Тесты для SetAvatarSerializer."""

    def test_validate_avatar_required(self):
        """Тест валидации обязательного поля avatar."""
        serializer = SetAvatarSerializer()

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_avatar(None)

        assert 'Поле avatar обязательно.' in str(exc_info.value)

    def test_validate_avatar_empty_string(self):
        """Тест валидации пустой строки в поле avatar."""
        serializer = SetAvatarSerializer()

        with pytest.raises(ValidationError) as exc_info:
            serializer.validate_avatar('')

        assert 'Поле avatar обязательно.' in str(exc_info.value)


@pytest.mark.django_db
class TestRecipeIngredientWriteSerializer:
    """Тесты для RecipeIngredientWriteSerializer."""

    def test_amount_validation_positive(self, ingredient):
        """Тест валидации положительного количества ингредиента."""
        data = {'id': ingredient.id, 'amount': 100}
        serializer = RecipeIngredientWriteSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data['amount'] == 100

    def test_amount_validation_zero(self, ingredient):
        """Тест валидации нулевого количества ингредиента."""
        data = {'id': ingredient.id, 'amount': 0}
        serializer = RecipeIngredientWriteSerializer(data=data)

        assert not serializer.is_valid()
        assert 'amount' in serializer.errors

    def test_amount_validation_negative(self, ingredient):
        """Тест валидации отрицательного количества ингредиента."""
        data = {'id': ingredient.id, 'amount': -1}
        serializer = RecipeIngredientWriteSerializer(data=data)

        assert not serializer.is_valid()
        assert 'amount' in serializer.errors
