from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """全局的分页类，所有的list请求会调用"""

    page_size = 10  # 每页显示的条数
    page_size_query_param = 'page_size'  # 前端发送的页数关键字名
    max_page_size = 20  # 每页最大显示的条数

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            # ('next', self.get_next_link()),
            # ('previous', self.get_previous_link()),
            # ('code', 0),
            # ('message', 'Ok'),
            ('results', data),
        ]))
