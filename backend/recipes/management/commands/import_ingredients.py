import csv
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from CSV or JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path to the ingredients file'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='csv',
            help='File format (csv or json)'
        )

    def handle(self, *args, **options):
        file_path = options.get('path') or os.path.join(
            settings.BASE_DIR.parent, 'data', 'ingredients.csv'
        )
        file_format = options.get('format')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(
                f'File {file_path} does not exist'
            ))
            return

        try:
            if file_format == 'csv':
                self._import_from_csv(file_path)
            elif file_format == 'json':
                self._import_from_json(file_path)
            else:
                self.stdout.write(self.style.ERROR(
                    f'Unknown format {file_format}'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

    def _import_from_csv(self, file_path):
        with open(file_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported ingredients from {file_path}'
            ))

    def _import_from_json(self, file_path):
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported ingredients from {file_path}'
            ))
