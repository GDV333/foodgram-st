from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для модели User."""
    search_fields = ('email', 'username')
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-панель для модели Subscription."""
    list_display = ('user', 'author')
