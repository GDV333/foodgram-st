# Фикстуры для разработки

Этот каталог содержит фикстуры данных для локальной разработки проекта Foodgram.

## Содержимое

### `ingredients_fixture.json`
JSON фикстура с данными ингредиентов:
- Содержит около 2188 ингредиентов с единицами измерения
- Используется как базовые данные для всех окружений
- Загружается автоматически скриптами разработки

## Использование

Фикстуры автоматически загружаются при выполнении:
```bash
./scripts/dev/reset_db.sh
./scripts/dev/start_server.sh
```

Для ручной загрузки:
```bash
cd backend
python manage.py loaddata ../fixtures/dev/ingredients_fixture.json
```

## Формат данных

Фикстура содержит объекты модели `recipes.Ingredient`:
```json
{
    "model": "recipes.ingredient",
    "pk": 1,
    "fields": {
        "name": "абрикосовое варенье",
        "measurement_unit": "г"
    }
}
```

## Добавление новых фикстур

Для создания новых фикстур используйте Django команду:
```bash
python manage.py dumpdata recipes.ingredient --indent 2 > fixtures/dev/new_fixture.json
```
