from rest_framework.views import exception_handler
from utils.response import msg
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    res = Response()
    if response is not None:
        res.data = msg(err=response.data['detail'])
    return res
