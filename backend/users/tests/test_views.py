import io
import pytest
from django.urls import reverse
from rest_framework import status
from users.models import Subscription
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


@pytest.mark.django_db
class TestUserAPI:
    """Тесты для API пользователей."""

    def test_user_list(self, authenticated_client):
        """Тест получения списка пользователей."""
        url = reverse('api:user-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
        assert 'avatar' in response.data['results'][0]

    def test_user_register(self, api_client):
        """Тест регистрации нового пользователя."""
        url = reverse('api:user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newPassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'newuser@example.com'
        assert 'password' not in response.data

    def test_user_current(self, authenticated_client, user):
        """Тест получения текущего пользователя."""
        url = reverse('api:user-me')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email
        assert 'avatar' in response.data

    def test_user_subscribe(self, authenticated_client, admin_user, user):
        """Тест подписки на автора."""
        url = reverse('api:user-subscribe', kwargs={'pk': admin_user.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert Subscription.objects.filter(user=user, author=admin_user).exists()
        assert 'recipes' in response.data
        assert 'recipes_count' in response.data

        # Тест отписки
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Subscription.objects.filter(user=user, author=admin_user).exists()

    def test_user_subscriptions(self, authenticated_client, admin_user, user):
        """Тест получения подписок пользователя."""
        # Создаем подписку
        Subscription.objects.create(user=user, author=admin_user)

        url = reverse('api:user-subscriptions')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1
        assert 'recipes' in response.data['results'][0]
        assert 'recipes_count' in response.data['results'][0]

    def test_avatar_put(self, authenticated_client):
        """Тест установки аватара пользователя через PUT."""
        url = reverse('api:user-avatar')

        # Создаем простое изображение 1x1 пиксель
        img = Image.new('RGB', (1, 1), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)

        avatar = SimpleUploadedFile(
            name='test_avatar.png',
            content=img_io.getvalue(),
            content_type='image/png'
        )

        data = {'avatar': avatar}
        response = authenticated_client.put(url, data, format='multipart')

        assert response.status_code == status.HTTP_200_OK
        assert 'avatar' in response.data
        assert response.data['avatar'] is not None

    def test_avatar_delete(self, authenticated_client, user):
        """Тест удаления аватара пользователя."""
        # Устанавливаем аватар сначала
        img = Image.new('RGB', (1, 1), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)

        avatar = SimpleUploadedFile(
            name='test_avatar.png',
            content=img_io.getvalue(),
            content_type='image/png'
        )
        user.avatar = avatar
        user.save()

        url = reverse('api:user-avatar')
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что аватар удален
        user.refresh_from_db()
        assert not user.avatar

    def test_avatar_invalid_data(self, authenticated_client):
        """Тест установки аватара с невалидными данными."""
        url = reverse('api:user-avatar')

        # Пытаемся загрузить не изображение
        invalid_file = SimpleUploadedFile(
            name='test.txt',
            content=b'not an image',
            content_type='text/plain'
        )

        data = {'avatar': invalid_file}
        response = authenticated_client.put(url, data, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_avatar_unauthenticated(self, api_client):
        """Тест попытки установки аватара неаутентифицированным пользователем."""
        url = reverse('api:user-avatar')

        img = Image.new('RGB', (1, 1), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)

        avatar = SimpleUploadedFile(
            name='test_avatar.png',
            content=img_io.getvalue(),
            content_type='image/png'
        )

        data = {'avatar': avatar}
        response = api_client.put(url, data, format='multipart')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
