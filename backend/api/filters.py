from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from django.contrib.auth import get_user_model

from recipes.models import Recipe

User = get_user_model()


class IngredientSearchFilter(SearchFilter):
    """Фильтр для поиска по названию ингредиента."""
    search_param = 'name'
    
    def filter_queryset(self, request, queryset, view):
        """
        Переопределенный метод фильтрации для поиска по префиксу.
        """
        search_terms = self.get_search_terms(request)
        if not search_terms:
            return queryset
        
        # Используем поиск по префиксу вместо поиска вхождения
        search_term = search_terms[0]  # Берем первый поисковый термин
        return queryset.filter(name__startswith=search_term)


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""
    author = filters.CharFilter(method='filter_author')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart')

    def filter_author(self, queryset, name, value):
        """Фильтрация по автору с валидацией ID."""
        if not value:
            return queryset
        try:
            # Проверяем, что значение можно преобразовать в int
            author_id = int(value)
            return queryset.filter(author_id=author_id)
        except (ValueError, TypeError):
            # Если ID невалидный (например, {{userId}}), возвращаем пустой queryset
            return queryset.none()

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по включению в избранное."""
        if not hasattr(self, 'request') or not self.request:
            return queryset
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorited__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по включению в список покупок."""
        if not hasattr(self, 'request') or not self.request:
            return queryset
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(in_shopping_cart__user=user)
        return queryset
