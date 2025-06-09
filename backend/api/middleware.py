class InvalidTokenFixMiddleware:
    """
    Middleware для исправления проблемы с невалидными токенами от фронтенда.
    Удаляет заголовки типа "Token null", "Token undefined" и т.п.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Исправляем проблему с невалидными токенами из фронтенда
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        # Проверяем различные варианты невалидных токенов
        invalid_tokens = ['null', 'undefined', 'none', '']
        if auth_header.startswith('Token '):
            token_value = auth_header.split(' ', 1)[1].strip().lower()
            if token_value in invalid_tokens:
                del request.META['HTTP_AUTHORIZATION']

        response = self.get_response(request)
        return response
