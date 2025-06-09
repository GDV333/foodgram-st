# Multi-stage build для оптимизации
FROM node:18-alpine AS build

WORKDIR /app

# Устанавливаем git если нужен для некоторых пакетов
RUN apk add --no-cache git

# Сначала копируем только файлы зависимостей для кеширования
COPY package*.json ./

# Очищаем npm кеш и устанавливаем зависимости
RUN npm cache clean --force && \
    npm install --legacy-peer-deps --no-audit --no-fund

# Теперь копируем остальные файлы
COPY . .

# Собираем приложение
RUN npm run build

# Production stage - только готовая сборка
FROM nginx:1.21.3-alpine
COPY --from=build /app/build /var/www/build
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
