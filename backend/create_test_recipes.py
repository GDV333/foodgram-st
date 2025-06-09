#!/usr/bin/env python3
"""
Скрипт для создания 12 тестовых рецептов от разных пользователей
"""

import os
import sys
import django

# Настройка Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from django.contrib.auth import get_user_model
from recipes.models import Recipe, Ingredient, RecipeIngredient
from random import choice, randint
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


def create_test_users():
    """Создаем тестовых пользователей"""
    users_data = [
        {'username': 'chef_alex', 'email': 'alex@foodgram.com', 'first_name': 'Александр', 'last_name': 'Петров'},
        {'username': 'maria_cook', 'email': 'maria@foodgram.com', 'first_name': 'Мария', 'last_name': 'Иванова'},
        {'username': 'pasta_lover', 'email': 'pasta@foodgram.com', 'first_name': 'Джованни', 'last_name': 'Россини'},
        {'username': 'sweet_baker', 'email': 'baker@foodgram.com', 'first_name': 'Анна', 'last_name': 'Кондитер'},
        {'username': 'meat_master', 'email': 'meat@foodgram.com', 'first_name': 'Дмитрий', 'last_name': 'Гриллов'},
        {'username': 'vegan_chef', 'email': 'vegan@foodgram.com', 'first_name': 'Елена', 'last_name': 'Зеленина'},
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
            }
        )
        if created:
            user.set_password('testpassword')
            user.save()
            print(f"✅ Создан пользователь: {user.username}")
        users.append(user)
    
    return users


def create_simple_image():
    """Создаем простое изображение для рецептов"""
    # Создаем простую картинку 1x1 пиксель (минимальное изображение)
    image_content = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
        b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
        b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342'
        b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11'
        b'\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14'
        b'\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00'
        b'\x3f\x00\xaa\xff\xd9'
    )
    
    return SimpleUploadedFile(
        name='test_recipe.jpg',
        content=image_content,
        content_type='image/jpeg'
    )


def create_test_recipes():
    """Создаем тестовые рецепты"""
    users = create_test_users()
    
    # Получаем случайные ингредиенты из базы
    all_ingredients = list(Ingredient.objects.all()[:20])  # Берем первые 20 ингредиентов
    
    if not all_ingredients:
        print("❌ Нет ингредиентов в базе. Загрузите сначала ингредиенты.")
        return
    
    recipes_data = [
        {
            'name': 'Классическая яичница',
            'text': 'Простой и быстрый завтрак. Разогреваем сковороду, добавляем масло, разбиваем яйца.',
            'cooking_time': 10,
            'ingredients_count': 3
        },
        {
            'name': 'Овощной салат',
            'text': 'Свежий салат из сезонных овощей с оливковым маслом.',
            'cooking_time': 15,
            'ingredients_count': 5
        },
        {
            'name': 'Спагетти болоньезе',
            'text': 'Классическая итальянская паста с мясным соусом.',
            'cooking_time': 45,
            'ingredients_count': 8
        },
        {
            'name': 'Шоколадный торт',
            'text': 'Нежный шоколадный торт с кремом.',
            'cooking_time': 120,
            'ingredients_count': 6
        },
        {
            'name': 'Говяжий стейк',
            'text': 'Сочный стейк средней прожарки с гарниром.',
            'cooking_time': 25,
            'ingredients_count': 4
        },
        {
            'name': 'Веганский суп',
            'text': 'Полезный суп из овощей без продуктов животного происхождения.',
            'cooking_time': 40,
            'ingredients_count': 7
        },
        {
            'name': 'Домашняя пицца',
            'text': 'Пицца на тонком тесте с любимой начинкой.',
            'cooking_time': 60,
            'ingredients_count': 10
        },
        {
            'name': 'Куриный суп',
            'text': 'Согревающий куриный суп с овощами.',
            'cooking_time': 90,
            'ingredients_count': 6
        },
        {
            'name': 'Фруктовый смузи',
            'text': 'Освежающий напиток из свежих фруктов.',
            'cooking_time': 5,
            'ingredients_count': 4
        },
        {
            'name': 'Рыбное филе в духовке',
            'text': 'Нежное рыбное филе, запеченное с травами.',
            'cooking_time': 35,
            'ingredients_count': 5
        },
        {
            'name': 'Овощное рагу',
            'text': 'Тушеные овощи в ароматных специях.',
            'cooking_time': 50,
            'ingredients_count': 8
        },
        {
            'name': 'Творожная запеканка',
            'text': 'Полезная запеканка на завтрак или ужин.',
            'cooking_time': 45,
            'ingredients_count': 6
        }
    ]
    
    created_count = 0
    for i, recipe_data in enumerate(recipes_data):
        author = users[i % len(users)]  # Циклически назначаем авторов
        
        try:
            # Проверяем, есть ли уже такой рецепт
            if Recipe.objects.filter(name=recipe_data['name']).exists():
                print(f"⚠️  Рецепт '{recipe_data['name']}' уже существует")
                continue
            
            recipe = Recipe.objects.create(
                author=author,
                name=recipe_data['name'],
                text=recipe_data['text'],
                cooking_time=recipe_data['cooking_time'],
                image=create_simple_image()
            )
            
            # Добавляем случайные ингредиенты
            recipe_ingredients = []
            selected_ingredients = []
            
            for _ in range(min(recipe_data['ingredients_count'], len(all_ingredients))):
                ingredient = choice([ing for ing in all_ingredients if ing not in selected_ingredients])
                selected_ingredients.append(ingredient)
                amount = randint(50, 500)  # Случайное количество от 50 до 500
                
                recipe_ingredients.append(RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                ))
            
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
            created_count += 1
            print(f"✅ Создан рецепт: {recipe.name} (автор: {author.username})")
            
        except Exception as e:
            print(f"❌ Ошибка при создании рецепта '{recipe_data['name']}': {e}")
    
    print(f"\n🎉 Создано {created_count} тестовых рецептов!")


if __name__ == '__main__':
    print("🍽️ Создание тестовых рецептов...")
    try:
        create_test_recipes()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
