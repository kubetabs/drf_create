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

### 授权

官方文档：`https://www.django-rest-framework.org/api-guide/permissions/`

`Django REST Framework提供的常见几种权限`

#### AllowAny

没有限制，无论请求是否做了认证

#### IsAuthenticated

请求必须做了认证

#### IsAdminUser

`admin`用户才有权限(user.is_staff = True)

#### IsAuthenticatedOrReadOnly

认证的用户有权限访问所有接口，未认证的用户只能访问只读接口(`GET` `HEAD` `OPTIONS`)

系统全局设置

```python
REST_FRAMEWORK = {
    # 权限
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

`viewset`的各action设置不同的权限

`apps/users/views.py`

```python
class UserViewSet(ModelViewSet):
    # ...
    permission_classes_by_action = {
        'create': [AllowAny],
    }
    # ...
    def get_permissions(self):
        try:
    	    return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
    	    return [permission() for permission in self.permission_classes]
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

`curl  http://127.0.0.1:8000/api/user/?page=1&page_size=3`

```json
{"status":"success","code":200,"data":{"count":13,"results":[{"id":1,"password":"pbkdf2_sha256$216000$vqNb07ePw5lH$RRvZJhCpKOB3stA9DVkem7SU3aA8fhEdvAg0/ymD6TM=","last_login":null,"is_superuser":true,"username":"admin","first_name":"","last_name":"","email":"admin@plsof.com","is_staff":true,"is_active":true,"date_joined":"2021-03-16T09:19:09.296545Z","telephone":"","groups":[],"user_permissions":[]},{"id":2,"password":"pbkdf2_sha256$216000$bYJzRb64QR1y$Mdrt7ArEORnDxbnCsF4jXSjkYPw1Gs3BDJ/sSgMXuZQ=","last_login":null,"is_superuser":false,"username":"p1","first_name":"","last_name":"","email":"p1@plsof.com","is_staff":false,"is_active":true,"date_joined":"2021-03-22T06:38:53.365624Z","telephone":null,"groups":[],"user_permissions":[]},{"id":3,"password":"pbkdf2_sha256$216000$3W00k9Zwgj10$yIPcWSQkvLozva2Kq+L1CvlLCaMnomoiszPtxTdRSeY=","last_login":null,"is_superuser":false,"username":"p2","first_name":"","last_name":"","email":"p2@plsof.com","is_staff":false,"is_active":true,"date_joined":"2021-03-22T06:40:21.859173Z","telephone":null,"groups":[],"user_permissions":[]}]},"message":null}
```



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
  	'EXCEPTION_HANDLER': 'common.rest_framework.custom_exception_handler'
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

Django3.0开始支持异步ASGI

### websocket

案例：查看日志文件最新内容（类型tail -f /tmp/xxx_log）

`drf_create/asgi.py`

```python
"""
ASGI config for drf_create project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from .websocket import log_consumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_create.settings')

django_application = get_asgi_application()


async def application(scope, receive, send):
    if scope['type'] == 'http':
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        await log_consumer(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")

```



`drf_create/websocket.py`

```python
import os
import tailer
import json
from django.conf import settings
from threading import Thread
import asyncio


async def tail_log(task_id, send):
    log_file_path = os.path.join(settings.DEPLOY_LOG_PATH, f'{task_id}_log')
    if os.path.exists(log_file_path):
        for line in tailer.follow(open(log_file_path)):
            await send({
                'type': 'websocket.send',
                'text': json.dumps(line)
            })
    else:
        await send({
            'type': 'websocket.send',
            'text': json.dumps(f'{log_file_path} not exist')
        })


async def log_consumer(scope, receive, send):

    while True:
        event = await receive()

        if event['type'] == 'websocket.connect':
            await send({
                'type': 'websocket.accept',
                'text': json.dumps("waiting for task log...")
            })

        if event['type'] == 'websocket.receive':
            task_id = json.loads(event['text']).get('task_id', None)

            if not task_id:
                await send({
                    'type': 'websocket.send',
                    'text': json.dumps("task_id为空，请输入task_id")
                })

            t = Thread(target=asyncio.run, args=(tail_log(task_id, send),))
            t.start()

        if event['type'] == 'websocket.disconnect':
            await send({
                'type': 'websocket.close'
            })
            break

```

运行

`uvicorn drf_create.asgi:application --reload --debug --ws websockets`

请求

`ws:127.0.0.1:8000`

```json
{"task_id": "123"}
```

