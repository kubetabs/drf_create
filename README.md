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



## 认证

这里我们使用`jwt`

`pip isntall djangorestframework-simplejwt`

关于`jwt`的介绍：`https://www.ruanyifeng.com/blog/2018/07/json_web_token-tutorial.html`

`drf_create/urls.py `

```python
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshSlidingView
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    # 登录接口
    path(r'api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # token刷新接口
    path(r'api/token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
    # token刷新接口
    path(r'api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
```

系统配置`jwt`

`drf_create/settings.py`

```python
REST_FRAMEWORK = {
    # 认证
    'DEFAULT_AUTHENTICATION_CLASSES': [
	    'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
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

前后端分离开发，需要一个统一的返回格式，这里是跟前端约定的返回格式

```json
{
	"status": "success",
	"code": 200,
	"data": {},
	"message": null
}
```

`status`: `http code 2xx` -> success 其余 error

`code`: http状态码

`data`: 返回数据

`message`: 返回消息，一般都是django默认的http 4xx，http 5xx（如果设置了异常处理）消息



这里使用`render`做统一格式的返回

`apps/common/rest_framework/render.py`

```python
from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        response = {
          "status": "success",
          "code": status_code,
          "data": data,
          "message": None
        }

        if not str(status_code).startswith('2'):
            response["status"] = "error"
            response["data"] = None
            try:
                if isinstance(data, dict):
                    response["message"] = data["detail"]
                if isinstance(data, str):
                    response["message"] = data
            except KeyError:
                response["data"] = data

        return super(CustomRenderer, self).render(response, accepted_media_type, renderer_context)

```

`apps/users/views.py`

```python
from common.rest_framework import CustomRenderer


class UserViewSet(ModelViewSet):

    # ...
    renderer_classes = [CustomRenderer]
    # ...
```

## 异常处理

官方文档：`https://www.django-rest-framework.org/api-guide/exceptions/`

`REST Framework`处理三种异常

+ `APIException`

+ `Http404`

+ `PermissionDenied`

如果你想在程序运行发生网关错误500的时候能返回自定义的格式，而不是页面报错，这个时候就可以自定义异常处理捕捉到这个500

`apps/common/rest_framework/exception.py`

  ```python
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
  
  ```

配置

`drf_create/settings.py`

```python
REST_FRAMEWORK = {
  	# 异常处理
  	# 'EXCEPTION_HANDLER': 'common.rest_framework.custom_exception_handler'
}
```

模拟

`apps/users/views.py`

```python
class UserViewSet(ModelViewSet):
  	# ...
    @action(detail=False, methods=['get'])
    def test(self, request, *args, **kwargs):
        print(acd)
        raise ValidationError({"detail": "here raise"})
```

`curl http://127.0.0.1:8000/api/user/test/`

```json
{
	"status": "error",
	"code": 500,
	"data": null,
	"message": "服务器异常"
}
```



## 异步

