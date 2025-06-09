import pytest
from django.contrib.auth import get_user_model
from users.authentication import EmailBackend

User = get_user_model()


@pytest.mark.django_db
class TestEmailBackend:
    """Тесты для кастомного backend аутентификации по email."""

    def test_authenticate_with_email_and_password_success(self):
        """Тест успешной аутентификации по email и паролю."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        backend = EmailBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='test@example.com',
            password='testpass123'
        )

        assert authenticated_user is not None
        assert authenticated_user == user

    def test_authenticate_with_wrong_email(self):
        """Тест аутентификации с несуществующим email."""
        backend = EmailBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='nonexistent@example.com',
            password='testpass123'
        )

        assert authenticated_user is None

    def test_authenticate_with_wrong_password(self):
        """Тест аутентификации с неправильным паролем."""
        User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        backend = EmailBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='test@example.com',
            password='wrongpassword'
        )

        assert authenticated_user is None

    def test_authenticate_with_inactive_user(self):
        """Тест аутентификации с неактивным пользователем."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_active=False
        )

        backend = EmailBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='test@example.com',
            password='testpass123'
        )

        assert authenticated_user is None
