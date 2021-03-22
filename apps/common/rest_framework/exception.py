from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
# import traceback


def custom_exception_handler(exc, context):
    """
    自定义的异常处理
    :param exc:     本次请求发送的异常信息
    :param context: 本次请求发送异常的执行上下文【本次请求的request对象，异常发送的时间，行号等....】
    :return:
    """

    response = exception_handler(exc, context)

    # 5xx错误
    if response is None:
        # trace_info = traceback.format_exc()
        response = Response('服务器异常', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
