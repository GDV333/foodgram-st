from django.contrib import admin

from .models import (
    Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель для модели Ingredient."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    ordering = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингредиентов в рецепте."""
    model = RecipeIngredient
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель для модели Recipe."""
    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('author', 'name')
    search_fields = ('name', 'author__username')
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('favorites_count',)

    def favorites_count(self, obj):
        """Количество добавлений рецепта в избранное."""
        return obj.favorited.count()

    favorites_count.short_description = 'В избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-панель для модели Favorite."""
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-панель для модели ShoppingCart."""
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
