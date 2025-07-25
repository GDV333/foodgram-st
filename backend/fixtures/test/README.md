# Фикстуры для тестирования

Этот каталог содержит фикстуры данных для автоматизированного тестирования проекта Foodgram.

## Содержимое

### `ingredients_fixture.json`
JSON фикстура с данными ингредиентов для тестов:
- Идентична фикстуре для разработки
- Обеспечивает стабильную тестовую среду
- Загружается автоматически при запуске Newman тестов

## Использование

Фикстуры автоматически загружаются при выполнении:
```bash
./scripts/tests/run_newman.sh
```

Для ручной загрузки в тестовом окружении:
```bash
cd backend
python manage.py loaddata ../fixtures/test/ingredients_fixture.json
```

## Особенности тестовых фикстур

- Данные должны быть стабильными и воспроизводимыми
- Содержат минимально необходимый набор для тестов
- Не должны изменяться без обновления соответствующих тестов
- Используются как для unit тестов, так и для API тестов

## Создание дополнительных тестовых данных

Тестовые пользователи и рецепты создаются динамически через Django management команду:
```bash
python manage.py create_test_data
```

Эта команда:
- Очищает существующие тестовые данные
- Создает предопределенных пользователей
- Создает тестовые рецепты с ингредиентами
- Обеспечивает стабильную тестовую среду
