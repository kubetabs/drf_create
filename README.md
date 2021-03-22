# Django Rest Frameowk脚手架

```shell
Python: 3.8.5
Django: 3.1.7
djangorestframework: 3.12.2
```



## 认证授权

### 自定义用户

Django默认提供了用户，如果如果你想添加自定义用户字段，这个时候就需要自定义用户表了

`apps/users/models.py`

```python
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    telephone = models.CharField(verbose_name="手机号码", max_length=11, blank=True, null=True)

    class Meta(AbstractUser.Meta):
        db_table = 'auth_user'
        ordering = ['id']

```



`apps/users/serializers.py`

```python
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
```



`apps/users/views.py`

```python
class UserViewSet(ModelViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    # ...
```

配置文件中添加

`drf_create/settings.py`

```python
# 自定义用户表
AUTH_USER_MODEL = 'users.User'
```



## 分页

设置系统默认分页

`drf_create/settings.py`

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

自定义用户分页

`apps/common/rest_framework/pagination.py`

```python
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

```

`apps/users/views.py`

```python
from common.rest_framework import CustomPagination


class UserViewSet(ModelViewSet):
		
    # ...
    pagination_class = CustomPagination
    # ...
```

请求第一页显示2个数据

`curl  http://127.0.0.1:8000/api/user/?page=1&page_size=2`



## 统一返回格式

## 异常处理

## 异步

