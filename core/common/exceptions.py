from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if response.status_code < 400:
            response.data = {
                "success": True,
                "message": response.data.get("detail", "با موفقیت انجام شد"),
            }
        else:
            response.data = {
                "success": False,
                "error": response.data.get("detail", "خطایی رخ داد"),
            }
    else:
        raise exc
    return response
