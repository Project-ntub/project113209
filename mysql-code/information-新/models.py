# app113209/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# 定義用戶模型
class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    verification_code = models.CharField(max_length=6, blank=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    department_id = models.CharField(max_length=10, blank=True)
    position_id = models.CharField(max_length=10, blank=True)
    branch_id = models.CharField(max_length=10, blank=True)
    otp_secret = models.CharField(maximum_length=32, blank=True)
    font_size = models.CharField(max_length=10, default='medium')
    notifications_enabled = models.BooleanField(default=True)
    auto_login_enabled = models.BooleanField(default=False)
    authentication_enabled = models.BooleanField(default=True)
    module_id = models.IntegerField(default=1)
