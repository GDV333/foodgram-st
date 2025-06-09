#!/bin/bash

# Скрипт для пуша образов в Docker Hub
# Использование: ./scripts/docker_push.sh [версия]

set -e

# Настройки
DOCKER_USERNAME="gdv001"
VERSION=${1:-"latest"}

# Имена образов в Docker Hub
BACKEND_IMAGE="${DOCKER_USERNAME}/foodgram-backend"
FRONTEND_IMAGE="${DOCKER_USERNAME}/foodgram-frontend"

echo "🐳 Подготовка образов для Docker Hub..."
echo "👤 Пользователь: ${DOCKER_USERNAME}"
echo "🏷️  Версия: ${VERSION}"
echo ""

# Проверяем авторизацию в Docker Hub (попробуем простой пуш)
echo "🔍 Проверяем авторизацию в Docker Hub..."

# Переходим в директорию infra
cd "$(dirname "$0")/../infra"

echo "🔍 Получаем ID существующих образов..."
BACKEND_ID=$(docker images -q infra-backend)
FRONTEND_ID=$(docker images -q infra-frontend)

if [ -z "$BACKEND_ID" ] || [ -z "$FRONTEND_ID" ]; then
    echo "❌ Образы не найдены! Сначала соберите их:"
    echo "   make docker-build"
    exit 1
fi

echo "✅ Найдены образы:"
echo "   Backend: $BACKEND_ID"
echo "   Frontend: $FRONTEND_ID"
echo ""

# Тегируем образы
echo "🏷️ Тегируем образы..."
docker tag infra-backend "${BACKEND_IMAGE}:${VERSION}"
docker tag infra-backend "${BACKEND_IMAGE}:latest"
docker tag infra-frontend "${FRONTEND_IMAGE}:${VERSION}"
docker tag infra-frontend "${FRONTEND_IMAGE}:latest"

echo "✅ Образы тегированы:"
echo "   ${BACKEND_IMAGE}:${VERSION}"
echo "   ${BACKEND_IMAGE}:latest"
echo "   ${FRONTEND_IMAGE}:${VERSION}"
echo "   ${FRONTEND_IMAGE}:latest"
echo ""

# Пушим образы
echo "📤 Пушим образы в Docker Hub..."
echo ""

echo "📤 Пуш backend образа..."
docker push "${BACKEND_IMAGE}:${VERSION}"
docker push "${BACKEND_IMAGE}:latest"

echo ""
echo "📤 Пуш frontend образа..."
docker push "${FRONTEND_IMAGE}:${VERSION}"
docker push "${FRONTEND_IMAGE}:latest"

echo ""
echo "🎉 Все образы успешно загружены в Docker Hub!"
echo ""
echo "🔗 Ссылки на образы:"
echo "   Backend:  https://hub.docker.com/r/${DOCKER_USERNAME}/foodgram-backend"
echo "   Frontend: https://hub.docker.com/r/${DOCKER_USERNAME}/foodgram-frontend"
echo ""
echo "🚀 Для использования в production обновите docker-compose.yml:"
echo "   backend:"
echo "     image: ${BACKEND_IMAGE}:${VERSION}"
echo "   frontend:"
echo "     image: ${FRONTEND_IMAGE}:${VERSION}"
echo ""
