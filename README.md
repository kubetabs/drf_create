# Django Rest Frameowk脚手架



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

## 统一返回格式

## 异常处理

## 异步

