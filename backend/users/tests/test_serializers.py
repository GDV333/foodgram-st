import pytest
from django.contrib.auth import get_user_model
from users.serializers import CustomUserCreateSerializer, CustomUserSerializer

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializers:
    """Тесты сериализаторов пользователей."""

    def test_user_create_serializer_valid(self):
        """Тест валидации данных для создания пользователя."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword123'
        }

        serializer = CustomUserCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_user_create_serializer_invalid_username(self):
        """Тест валидации с невалидным username."""
        # Создаем пользователя для проверки дублирования
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            password='existingpassword'
        )

        data = {
            'username': 'existinguser',  # Уже существует
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword123'
        }

        serializer = CustomUserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_user_create_serializer_invalid_email(self):
        """Тест валидации с невалидным email."""
        # Создаем пользователя для проверки дублирования
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            password='existingpassword'
        )

        data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # Уже существует
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword123'
        }

        serializer = CustomUserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_custom_user_serializer(self, user):
        """Тест сериализации пользователя."""
        serializer = CustomUserSerializer(user)

        assert serializer.data['username'] == user.username
        assert serializer.data['email'] == user.email
        assert 'password' not in serializer.data
        assert 'avatar' in serializer.data
