from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
import logging

from recipes.models import (
    Ingredient, Recipe, Favorite, ShoppingCart, RecipeIngredient
)
from users.models import Subscription
from .serializers import (
    IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, SubscriptionSerializer,
    CustomUserSerializer, ShortRecipeSerializer, SetAvatarSerializer
)
# from .serializers import ( # Temporarily excluding IngredientSerializer
#     RecipeSerializer,
#     RecipeCreateSerializer, FavoriteSerializer,
#     ShoppingCartSerializer, SubscriptionSerializer, CustomUserSerializer
# )
from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPageNumberPagination

User = get_user_model()

# Логгеры для отладки
logger = logging.getLogger('api')
recipe_logger = logging.getLogger('recipes')
user_logger = logging.getLogger('users')


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Пользовательское разрешение для редактирования только авторами рецептов.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение предоставляются для любого запроса,
        # поэтому мы всегда разрешаем GET, HEAD или OPTIONS запросы.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешения на запись предоставляются только автору рецепта.
        return obj.author == request.user


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""
    queryset = Recipe.objects.all()
    permission_classes = (permissions.AllowAny,)  # Разрешаем все, проверки делаем вручную
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def create(self, request, *args, **kwargs):
        # Проверяем аутентификацию (401)
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Валидируем данные и создаем объект
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"detail": "Рецепт не найден."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        print(f"🔍 UPDATE: User={request.user.id if request.user.is_authenticated else 'Anonymous'}, Recipe ID={kwargs.get('pk')}")
        
        try:
            # Сначала проверяем существование объекта (404)
            instance = self.get_object()
            print(f"📋 Recipe found: ID={instance.id}, Author={instance.author.id}")
        except Http404:
            print("❌ Recipe not found - returning 404")
            return Response(
                {"detail": "Рецепт не найден."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем аутентификацию (401)
        if not request.user.is_authenticated:
            print("❌ User not authenticated - returning 401")
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Проверяем права доступа (403)
        if instance.author != request.user:
            print(f"🚫 Permission denied: Recipe author={instance.author.id}, Request user={request.user.id} - returning 403")
            return Response(
                {"detail": "У вас недостаточно прав для выполнения данного действия."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        print("✅ Permission check passed - updating recipe")
        try:
            # Валидируем данные (400)
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(f"💥 Update error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        print(f"🔍 DESTROY: User={request.user.id if request.user.is_authenticated else 'Anonymous'}, Recipe ID={kwargs.get('pk')}")
        
        try:
            # Сначала проверяем существование объекта (404)
            instance = self.get_object()
            print(f"📋 Recipe found: ID={instance.id}, Author={instance.author.id}")
        except Http404:
            print("❌ Recipe not found - returning 404")
            return Response(
                {"detail": "Рецепт не найден."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем аутентификацию (401)
        if not request.user.is_authenticated:
            print("❌ User not authenticated - returning 401")
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Проверяем права доступа (403)
        if instance.author != request.user:
            print(f"🚫 Permission denied: Recipe author={instance.author.id}, Request user={request.user.id} - returning 403")
            return Response(
                {"detail": "У вас недостаточно прав для выполнения данного действия."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        print("✅ Permission check passed - deleting recipe")
        try:
            # Выполняем удаление
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"💥 Destroy error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавить/удалить рецепт из избранного."""
        try:
            # Проверка валидности ID рецепта
            try:
                recipe_id = int(pk)
            except (ValueError, TypeError):
                return Response(
                    {"detail": "Некорректный ID рецепта."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe = get_object_or_404(Recipe, pk=recipe_id)

            if request.method == 'POST':
                # Проверяем, не добавлен ли уже рецепт в избранное
                if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
                    return Response(
                        {"detail": "Рецепт уже в избранном."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Добавляем рецепт в избранное
                favorite = Favorite.objects.create(user=request.user, recipe=recipe)
                serializer = ShortRecipeSerializer(recipe, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            elif request.method == 'DELETE':
                # Проверяем, есть ли рецепт в избранном
                try:
                    favorite = Favorite.objects.get(user=request.user, recipe=recipe)
                    favorite.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                except Favorite.DoesNotExist:
                    return Response(
                        {"detail": "Рецепт не в избранном."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        except Http404:
            return Response(
                {"detail": "Рецепт не найден."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавить/удалить рецепт из корзины покупок."""
        try:
            # Проверка валидности ID рецепта
            try:
                recipe_id = int(pk)
            except (ValueError, TypeError):
                return Response(
                    {"detail": "Некорректный ID рецепта."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe = get_object_or_404(Recipe, pk=recipe_id)

            if request.method == 'POST':
                # Проверяем, не добавлен ли уже рецепт в корзину
                if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
                    return Response(
                        {"detail": "Рецепт уже в списке покупок."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Добавляем рецепт в корзину покупок
                cart_item = ShoppingCart.objects.create(user=request.user, recipe=recipe)
                serializer = ShortRecipeSerializer(recipe, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            elif request.method == 'DELETE':
                # Проверяем, есть ли рецепт в корзине покупок
                try:
                    cart_item = ShoppingCart.objects.get(
                        user=request.user, recipe=recipe
                    )
                    cart_item.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                except ShoppingCart.DoesNotExist:
                    return Response(
                        {"detail": "Рецепт не в списке покупок."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        except Http404:
            return Response(
                {"detail": "Рецепт не найден или не в списке покупок."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        try:
            shopping_cart = ShoppingCart.objects.filter(user=request.user)
            recipes = [item.recipe for item in shopping_cart]

            if not recipes:
                return Response(
                    {'errors': 'В списке покупок нет рецептов'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ingredients = RecipeIngredient.objects.filter(
                recipe__in=recipes
            ).values(
                'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(
                total_amount=Sum('amount')
            ).order_by('ingredient__name')

            shopping_list = 'Список покупок:\n\n'
            for item in ingredients:
                shopping_list += (
                    f"{item['ingredient__name']} "
                    f"({item['ingredient__measurement_unit']}) — "
                    f"{item['total_amount']}\n"
                )

            response = HttpResponse(
                shopping_list, content_type='text/plain; charset=utf-8'
            )
            response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
            return response
        except Exception as e:
            return Response(
                {'errors': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Получить короткую ссылку на рецепт."""
        try:
            # Проверка валидности ID рецепта
            try:
                recipe_id = int(pk)
            except (ValueError, TypeError):
                return Response(
                    {"detail": "Некорректный ID рецепта."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe = get_object_or_404(Recipe, pk=recipe_id)
            # Формируем короткую ссылку
            short_link = f"{request.build_absolute_uri('/recipes/')}{recipe_id}/"
            return Response({"short-link": short_link})
        except Http404:
            return Response(
                {"detail": "Рецепт не найден."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с пользователями."""
    queryset = User.objects.all().order_by('id')
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            from users.serializers import CustomUserCreateSerializer  # Changed import path
            return CustomUserCreateSerializer
        return CustomUserSerializer

    def get_permissions(self):
        """Переопределение разрешений для создания пользователей."""
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None):
        """Получить пользователя по ID с валидацией."""
        try:
            # Проверяем, что pk можно преобразовать в int
            user_id = int(pk)
            user = get_object_or_404(User, pk=user_id)
        except (ValueError, TypeError):
            # Если ID невалидный (например, {{userId}}), возвращаем 400
            return Response(
                {'detail': 'Некорректный ID пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Получить информацию о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Управление аватаром текущего пользователя."""

        if request.method == 'PUT':
            serializer = SetAvatarSerializer(data=request.data)
            if serializer.is_valid():
                request.user.avatar = serializer.validated_data['avatar']
                request.user.save()
                return Response({
                    'avatar': request.user.avatar.url if request.user.avatar else None
                })
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            if request.user.avatar:
                request.user.avatar.delete()
                request.user.avatar = None
                request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        # Проверка обязательных полей
        if not current_password or not new_password:
            return Response(
                {'errors': 'Необходимо указать текущий и новый пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка текущего пароля
        if not user.check_password(current_password):
            return Response(
                {'errors': 'Неверный текущий пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Установка нового пароля
        user.set_password(new_password)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписаться/отписаться от автора."""
        try:
            author_id = int(pk)
            author = get_object_or_404(User, pk=author_id)
        except (ValueError, TypeError):
            # Если ID невалидный, возвращаем 400
            return Response(
                {'errors': 'Некорректный ID пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user == author:
            return Response(
                {'errors': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(
                user=request.user, author=author
            )
            if created:
                serializer = SubscriptionSerializer(
                    author, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = Subscription.objects.filter(
            user=request.user, author=author
        ).first()
        if not subscription:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        """Получить список подписок пользователя."""
        # Находим всех авторов, на которых подписан пользователь
        authors = User.objects.filter(
            subscribed__user=request.user
        ).order_by('id')

        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)


