import base64
import uuid

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipe,
                            ShoppingCart)
from users.models import User, Subscription


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для обработки изображений в формате Base64."""

    def to_internal_value(self, data):
        """Преобразует строку Base64 в файл изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            # Генерируем уникальное имя файла
            filename = f'{uuid.uuid4()}.{ext}'
            data = ContentFile(base64.b64decode(imgstr), name=filename)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User с полем is_subscribed."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь
        на данного пользователя."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient (промежуточная)."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное текущим пользователем."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в список покупок текущим пользователем."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'image', 'name', 'text',
            'cooking_time', 'author'
        )

    def validate_ingredients(self, value):
        """Проверяет, что ингредиенты указаны и не повторяются."""
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один ингредиент.'
            )
        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError('Ингредиенты не должны повторяться.')
        return value

    def validate_cooking_time(self, value):
        """Проверяет, что время приготовления больше 0."""
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0.'
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Создает новый рецепт с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self._create_ingredients_in_recipe(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет существующий рецепт и его ингредиенты."""
        ingredients_data = validated_data.pop('ingredients', None)

        # Проверяем, что ингредиенты указаны при обновлении
        if ingredients_data is None:
            raise serializers.ValidationError({
                'ingredients': 'Это поле обязательно.'
            })

        # Обновляем основные поля рецепта
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if 'image' in validated_data:  # Проверяем наличие ключа 'image'
            instance.image = validated_data.get('image', instance.image)
        instance.save()

        # Обновляем ингредиенты
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self._create_ingredients_in_recipe(instance, ingredients_data)

        return instance

    def _create_ingredients_in_recipe(self, recipe, ingredients_data):
        """Создает записи ингредиентов для рецепта."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients_data
        ])

    def to_representation(self, instance):
        """Возвращает представление рецепта с использованием RecipeReadSerializer."""
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления рецепта (для избранного и подписок)."""
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User  # Используем User как основу для вывода автора
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'avatar',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        """Всегда True, так как это сериализатор для подписок."""
        return True

    def get_recipes(self, obj):
        """Получает рецепты автора с ограничением по параметру recipes_limit."""
        request = self.context.get('request')
        recipes_limit = None

        if request:
            # Пробуем query_params (DRF Request) и GET (Django HttpRequest)
            if hasattr(request, 'query_params'):
                recipes_limit = request.query_params.get('recipes_limit')
            elif hasattr(request, 'GET'):
                recipes_limit = request.GET.get('recipes_limit')

        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                # Если recipes_limit невалидный, игнорируем его
                pass
        return ShortRecipeSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        """Получает общее количество рецептов автора."""
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления/удаления рецепта в/из избранного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """Проверяет, что рецепт не добавляется в избранное повторно."""
        request = self.context.get('request')
        recipe = data['recipe']
        if request and request.user.is_authenticated:
            if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепт уже в избранном.'}
                )
        return data

    def to_representation(self, instance):
        """Возвращает краткое представление рецепта при добавлении в избранное."""
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления/удаления рецепта в/из списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        """Проверяет, что рецепт не добавляется в список покупок повторно."""
        request = self.context.get('request')
        recipe = data['recipe']
        if request and request.user.is_authenticated:
            if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепт уже в списке покупок.'}
                )
        return data

    def to_representation(self, instance):
        """Возвращает краткое представление рецепта при добавлении в список покупок."""
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class SetAvatarSerializer(serializers.Serializer):
    """Сериализатор для установки аватара пользователя."""
    avatar = Base64ImageField(required=True)

    def validate_avatar(self, value):
        """Валидация изображения аватара."""
        if not value:
            raise serializers.ValidationError("Поле avatar обязательно.")
        return value
