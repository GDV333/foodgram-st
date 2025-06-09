import io
import pytest
from django.urls import reverse
from rest_framework import status
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import Subscription


@pytest.mark.django_db
class TestUserActions:
    """Тесты для действий пользователей в UserViewSet."""

    def test_user_retrieve_success(self, api_client, user):
        """Тест успешного получения пользователя по ID."""
        url = reverse('api:user-detail', kwargs={'pk': user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email

    def test_user_retrieve_invalid_id(self, api_client):
        """Тест получения пользователя с некорректным ID."""
        url = reverse('api:user-detail', kwargs={'pk': 'invalid'})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'detail' in response.data
        assert response.data['detail'] == 'Некорректный ID пользователя'

    def test_user_retrieve_nonexistent(self, api_client):
        """Тест получения несуществующего пользователя."""
        url = reverse('api:user-detail', kwargs={'pk': 99999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_set_password_success(self, authenticated_client, user):
        """Тест успешной смены пароля."""
        # Используем правильный пароль пользователя
        user.set_password('testpassword')
        user.save()
        authenticated_client.force_authenticate(user=user)

        url = reverse('api:user-set-password')
        data = {
            'current_password': 'testpassword',
            'new_password': 'newpassword123'
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что пароль действительно изменился
        user.refresh_from_db()
        assert user.check_password('newpassword123')

    def test_set_password_missing_current(self, authenticated_client):
        """Тест смены пароля без указания текущего пароля."""
        url = reverse('api:user-set-password')
        data = {'new_password': 'newpassword123'}
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'current_password' in response.data
        assert 'Обязательное поле' in str(response.data['current_password'])

    def test_set_password_missing_new(self, authenticated_client, user):
        """Тест смены пароля без указания нового пароля."""
        user.set_password('testpassword')
        user.save()
        authenticated_client.force_authenticate(user=user)

        url = reverse('api:user-set-password')
        data = {'current_password': 'testpassword'}
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'new_password' in response.data
        assert 'Обязательное поле' in str(response.data['new_password'])

    def test_set_password_wrong_current(self, authenticated_client, user):
        """Тест смены пароля с неверным текущим паролем."""
        user.set_password('testpassword')
        user.save()
        authenticated_client.force_authenticate(user=user)

        url = reverse('api:user-set-password')
        data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'current_password' in response.data
        assert 'Неправильный пароль' in str(response.data['current_password'])

    def test_set_password_unauthenticated(self, api_client):
        """Тест смены пароля неаутентифицированным пользователем."""
        url = reverse('api:user-set-password')
        data = {
            'current_password': 'password123',
            'new_password': 'newpassword123'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_avatar_put_success(self, authenticated_client, user):
        """Тест успешной установки аватара через PUT."""
        url = reverse('api:user-avatar')

        # Создаем изображение
        img = Image.new('RGB', (100, 100), color='blue')
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

        # Проверяем, что аватар действительно сохранился
        user.refresh_from_db()
        assert user.avatar is not None

    def test_avatar_put_invalid_file(self, authenticated_client):
        """Тест установки аватара с невалидным файлом."""
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

    def test_avatar_delete_success(self, authenticated_client, user):
        """Тест успешного удаления аватара."""
        # Сначала устанавливаем аватар
        img = Image.new('RGB', (100, 100), color='green')
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

    def test_avatar_delete_no_avatar(self, authenticated_client, user):
        """Тест удаления аватара, когда его нет."""
        url = reverse('api:user-avatar')
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_avatar_unauthenticated(self, api_client):
        """Тест попытки управления аватаром неаутентифицированным пользователем."""
        url = reverse('api:user-avatar')

        # PUT запрос
        img = Image.new('RGB', (100, 100), color='red')
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

        # DELETE запрос
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_subscribe_invalid_user_id(self, authenticated_client):
        """Тест подписки с некорректным ID пользователя."""
        url = reverse('api:user-subscribe', kwargs={'pk': 'invalid'})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert response.data['errors'] == 'Некорректный ID пользователя'

    def test_subscribe_self(self, authenticated_client, user):
        """Тест попытки подписки на самого себя."""
        url = reverse('api:user-subscribe', kwargs={'pk': user.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert response.data['errors'] == 'Нельзя подписаться на себя'

    def test_subscribe_already_subscribed(self, authenticated_client, user, admin_user):
        """Тест повторной подписки на пользователя."""
        # Создаем подписку
        Subscription.objects.create(user=user, author=admin_user)

        url = reverse('api:user-subscribe', kwargs={'pk': admin_user.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert response.data['errors'] == 'Вы уже подписаны на этого пользователя'

    def test_unsubscribe_not_subscribed(self, authenticated_client, admin_user):
        """Тест отписки от пользователя, на которого не подписан."""
        url = reverse('api:user-subscribe', kwargs={'pk': admin_user.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert response.data['errors'] == 'Вы не подписаны на этого пользователя'

    def test_subscribe_nonexistent_user(self, authenticated_client):
        """Тест подписки на несуществующего пользователя."""
        url = reverse('api:user-subscribe', kwargs={'pk': 99999})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_subscribe_unauthenticated(self, api_client, admin_user):
        """Тест попытки подписки неаутентифицированным пользователем."""
        url = reverse('api:user-subscribe', kwargs={'pk': admin_user.id})
        response = api_client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_subscriptions_unauthenticated(self, api_client):
        """Тест получения подписок неаутентифицированным пользователем."""
        url = reverse('api:user-subscriptions')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_unauthenticated(self, api_client):
        """Тест получения текущего пользователя неаутентифицированным пользователем."""
        url = reverse('api:user-me')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
