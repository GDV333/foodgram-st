# Multi-stage build для оптимизации
FROM node:18-alpine AS dependencies

WORKDIR /app

# Устанавливаем git если нужен для некоторых пакетов
RUN apk add --no-cache git

# Сначала копируем только файлы зависимостей для кеширования
COPY package*.json ./

# Устанавливаем зависимости с оптимизацией для Docker кеширования
# Используем npm install с --legacy-peer-deps для совместимости
RUN npm install --legacy-peer-deps --no-audit --no-fund --cache .npm \
    && npm cache clean --force

# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Копируем установленные зависимости из предыдущего stage
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=dependencies /app/package*.json ./

# Теперь копируем остальные файлы
COPY . .

# Собираем приложение с оптимизацией
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false
RUN npm run build

# Production stage - только готовая сборка
FROM nginx:1.21.3-alpine
COPY --from=build /app/build /var/www/build
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
