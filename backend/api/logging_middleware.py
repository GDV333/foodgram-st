"""
Middleware для логирования запросов и отладки
"""
import logging
import time
import traceback

logger = logging.getLogger('api.middleware')


class LoggingMiddleware:
    """Middleware для логирования всех запросов"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Логируем входящий запрос
        logger.info(
            f"Запрос: {request.method} {request.path} "
            f"от IP: {self.get_client_ip(request)} "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
        )

        # Логируем тело запроса для POST/PUT запросов
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if hasattr(request, 'body') and request.body:
                    logger.debug(f"Тело запроса: {request.body.decode('utf-8')[:1000]}")
            except Exception as e:
                logger.warning(f"Не удалось прочитать тело запроса: {e}")

        # Логируем GET параметры
        if request.GET:
            logger.debug(f"GET параметры: {dict(request.GET)}")

        # Обрабатываем запрос
        response = self.get_response(request)

        # Считаем время выполнения
        duration = time.time() - start_time

        # Логируем ответ
        logger.info(
            f"Ответ: {response.status_code} для {request.method} {request.path} "
            f"за {duration:.3f}с"
        )

        # Логируем детали ошибок
        if response.status_code >= 400:
            logger.warning(
                f"Ошибка {response.status_code}: {request.method} {request.path}"
            )

        if response.status_code >= 500:
            logger.error(
                f"Серверная ошибка {response.status_code}: {request.method} {request.path}"
            )

        return response

    def process_exception(self, request, exception):
        """Логируем необработанные исключения"""
        logger.error(
            f"Необработанное исключение для {request.method} {request.path}: "
            f"{exception.__class__.__name__}: {str(exception)}"
        )
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

    @staticmethod
    def get_client_ip(request):
        """Получаем IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DatabaseQueryLoggingMiddleware:
    """Middleware для логирования SQL запросов"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.sql_logger = logging.getLogger('django.db.backends')

    def __call__(self, request):
        from django.db import connection

        # Считаем количество запросов до
        queries_before = len(connection.queries)

        response = self.get_response(request)

        # Считаем количество запросов после
        queries_after = len(connection.queries)
        queries_count = queries_after - queries_before

        if queries_count > 0:
            self.sql_logger.info(
                f"SQL запросов для {request.method} {request.path}: {queries_count}"
            )

            # Логируем медленные запросы
            for query in connection.queries[queries_before:]:
                duration = float(query.get('time', 0))
                if duration > 0.1:  # Запросы дольше 100ms
                    self.sql_logger.warning(
                        f"Медленный запрос ({duration:.3f}s): {query['sql'][:200]}..."
                    )

        return response
