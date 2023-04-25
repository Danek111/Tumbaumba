from rest_framework.views import exception_handler


def custom_authentication_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if response.status_code == 401:
            response.status_code = 403
            response.data = {
                "code": 403,
                "message": "Ошибка логина"
            }
        elif response.status_code == 403:
            response.status_code = 403
            response.data = {
                "code": 403,
                "message": "Запрет доступа"
            }
        return response
