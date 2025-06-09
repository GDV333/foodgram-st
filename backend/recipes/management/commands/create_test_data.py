"""
Management command для создания базовых данных для тестирования API.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Команда для создания базовых данных для Newman тестов."""

    help = 'Создает базовые данные для Newman тестов'

    def handle(self, *args, **options):
        """Основная логика команды."""
        self.stdout.write('Инициализация базовых данных для Newman тестов...')

        self.stdout.write(
            self.style.SUCCESS('Базовая инициализация для Newman тестов завершена!')
        )
        self.stdout.write(
            self.style.WARNING('Пользователи и рецепты создаются Newman тестами через API!')
        )
