# app113209/signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from app113209.utils import record_history
from app113209.models import User


@receiver(user_logged_in, sender=User)
def log_user_login(sender, request, user, **kwargs):
    record_history(user.id, f"用戶 {user.username} 登入了系統")

@receiver(user_logged_out, sender=User)
def log_user_logout(sender, request, user, **kwargs):
    if user:  # 因為匿名使用者登出時 user 可能為 None
        record_history(user.id, f"用戶 {user.username} 登出了系統")
