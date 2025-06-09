from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import re

from .models import Subscription

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(
        max_length=150,  # Важно указать max_length, если он есть в модели
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Этот логин уже занят, попробуйте другой.'
            )
        ]
    )
    email = serializers.EmailField(
        max_length=254,  # Стандартная максимальная длина для EmailField
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже существует.'
            )
        ]
    )

    def validate_username(self, value):
        """Валидация username по регулярному выражению."""
        pattern = r'^[\w.@+-]+$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                'Имя пользователя может содержать только буквы, цифры и знаки @/./+/-/_'
            )
        return value

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return False
        user = request.user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()
