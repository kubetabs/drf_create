from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    telephone = models.CharField(verbose_name="手机号码", max_length=11, blank=True, null=True)

    class Meta(AbstractUser.Meta):
        db_table = 'auth_user'
        ordering = ['id']
