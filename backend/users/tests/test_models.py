import pytest
from django.contrib.auth import get_user_model
from users.models import Subscription

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Тесты для модели пользователя."""

    def test_user_str(self, user):
        """Тест строкового представления пользователя."""
        assert str(user) == user.email

    def test_user_create(self):
        """Тест создания пользователя."""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            first_name='New',
            last_name='User',
            password='newpassword123'
        )

        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.check_password('newpassword123')


@pytest.mark.django_db
class TestSubscriptionModel:
    """Тесты для модели подписки."""

    def test_subscription_create(self, user, admin_user):
        """Тест создания подписки."""
        subscription = Subscription.objects.create(
            user=user,
            author=admin_user
        )

        assert subscription.user == user
        assert subscription.author == admin_user

    def test_subscription_unique_constraint(self, user, admin_user):
        """Тест ограничения уникальности подписки."""
        # Создаем первую подписку
        Subscription.objects.create(user=user, author=admin_user)

        # Пытаемся создать дубликат
        with pytest.raises(Exception):
            Subscription.objects.create(user=user, author=admin_user)

    def test_subscription_str(self, user, admin_user):
        """Тест строкового представления подписки."""
        subscription = Subscription.objects.create(
            user=user,
            author=admin_user
        )

        expected_str = f"{user.email} подписан на {admin_user.email}"
        assert str(subscription) == expected_str
