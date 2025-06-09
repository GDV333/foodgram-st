#!/usr/bin/env python3
"""
Скрипт для запуска тестов API Foodgram.
Использует pytest для тестирования Django-приложений.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def get_project_root():
    """Возвращает корневую директорию проекта."""
    return Path(__file__).parent.parent.parent


def setup_environment():
    """Настраивает переменные окружения для тестов."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')


def parse_arguments():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(description='Запуск тестов Foodgram API')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Показывать расширенный вывод тестов')
    parser.add_argument('--coverage', '-c', action='store_true',
                        help='Показывать покрытие кода тестами')
    parser.add_argument('--app', '-a', type=str,
                        help='Тестировать указанное приложение (api, recipes или users)')
    parser.add_argument('--failfast', '-x', action='store_true',
                        help='Остановить тесты после первой ошибки')
    return parser.parse_args()


def run_tests(args):
    """Запускает тесты с учетом аргументов командной строки."""
    setup_environment()
    
    # Переходим в директорию backend
    backend_dir = get_project_root() / 'backend'
    os.chdir(backend_dir)
    
    # Формируем команду для запуска тестов
    command = ['python', '-m', 'pytest']
    
    # Добавляем опции в зависимости от аргументов
    if args.verbose:
        command.append('-v')
    
    if args.failfast:
        command.append('-x')
    
    if args.coverage:
        command.extend(['--cov=.', '--cov-report=term-missing', '--cov-report=html'])
    
    # Определяем, какие приложения тестировать
    if args.app:
        if args.app not in ['api', 'recipes', 'users']:
            print(f"Ошибка: неизвестное приложение '{args.app}'.")
            print("Допустимые значения: api, recipes, users")
            return False
        command.append(f'{args.app}/tests/')
    
    # Запускаем тесты
    print(f"Запуск команды: {' '.join(command)}")
    print(f"Рабочая директория: {os.getcwd()}")
    return subprocess.call(command) == 0


def main():
    """Основная функция скрипта."""
    args = parse_arguments()
    success = run_tests(args)
    
    if success:
        print("\n✅ Все тесты выполнены успешно!")
        return 0
    else:
        print("\n❌ Тесты выполнены с ошибками.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
