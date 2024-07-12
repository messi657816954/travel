from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # If the response has data, it means it's a recognized exception
        if isinstance(exc, (AuthenticationFailed, InvalidToken)):
            res = reponses(success=0, error_msg="AuthenticationFailed")
            return Response(res)

    return response

def reponses(success, num_page=None, results=None, error_msg=None):
    RESPONSE_MSG = [{'success': success}]

    if num_page:
        RESPONSE_MSG[0].update({'nombre_page': num_page})
    if results:
        if isinstance(results, list):
            RESPONSE_MSG[0].update({'results': results})
        else:
            RESPONSE_MSG[0].update({'results': [results]})
    if error_msg:
        RESPONSE_MSG[0].update({'errors': [{'error_msg': error_msg}]})

    return RESPONSE_MSG
