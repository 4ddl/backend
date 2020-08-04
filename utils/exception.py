from rest_framework.views import exception_handler
from rest_framework.response import Response
from .response import msg


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None and response.status_code in [400, 401, 403, 404, 405]:
        if isinstance(response.data, str) or isinstance(response.data, list):
            return Response(msg(err=response.data))
        else:
            return Response(msg(err=response.data['detail']))
    return response
