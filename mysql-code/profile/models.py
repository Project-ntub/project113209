from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    department_id = models.CharField(max_length=50, blank=True, null=True)
    position_id = models.CharField(max_length=50, blank=True, null=True)
    branch_id = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    expiry_time = models.DateTimeField(blank=True, null=True)
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    font_size = models.CharField(max_length=10, blank=True, null=True)
    notifications_enabled = models.BooleanField(default=True)
    auto_login_enabled = models.BooleanField(default=True)
    authentication_enabled = models.BooleanField(default=True)
    module_id = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.username
