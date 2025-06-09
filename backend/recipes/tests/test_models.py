import pytest
from django.contrib.auth import get_user_model
from recipes.models import Ingredient, Recipe, RecipeIngredient

User = get_user_model()


@pytest.mark.django_db
class TestIngredientModel:
    """Тесты для модели Ingredient."""

    def test_ingredient_str(self):
        """Тест строкового представления ингредиента."""
        ingredient = Ingredient.objects.create(
            name='Соль', measurement_unit='г'
        )
        assert str(ingredient) == 'Соль, г'

    def test_ingredient_unique_constraint(self):
        """Тест ограничения уникальности ингредиентов."""
        Ingredient.objects.create(name='Перец', measurement_unit='г')

        with pytest.raises(Exception):  # Должно быть нарушение уникальности
            Ingredient.objects.create(name='Перец', measurement_unit='г')


@pytest.mark.django_db
class TestRecipeModel:
    """Тесты для модели Recipe."""

    def test_recipe_str(self, user, small_gif):
        """Тест строкового представления рецепта."""
        recipe = Recipe.objects.create(
            author=user,
            name='Омлет',
            image=small_gif,
            text='Рецепт омлета',
            cooking_time=10
        )
        assert str(recipe) == 'Омлет'

    def test_recipe_ingredients(self, user, small_gif):
        """Тест добавления ингредиентов в рецепт."""
        # Создаем ингредиенты
        ingredient1 = Ingredient.objects.create(
            name='Яйцо', measurement_unit='шт'
        )
        ingredient2 = Ingredient.objects.create(
            name='Масло', measurement_unit='г'
        )

        # Создаем рецепт
        recipe = Recipe.objects.create(
            author=user,
            name='Омлет',
            image=small_gif,
            text='Рецепт омлета',
            cooking_time=10
        )

        # Добавляем ингредиенты в рецепт
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient1, amount=3
        )
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient2, amount=20
        )

        # Проверяем, что ингредиенты связаны с рецептом
        ingredients = recipe.ingredients.all()
        assert ingredient1 in ingredients
        assert ingredient2 in ingredients

        # Проверяем количество ингредиентов
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        assert recipe_ingredients.count() == 2
