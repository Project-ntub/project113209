# app113209\signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from app113209.utils import record_history
from app113209.models import User
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in, sender=User)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"User {user.username} logged in.")
    print(f"User {user.username} logged in.")
    record_history(user, f"用戶 {user.username} 登入了系統")

@receiver(user_logged_out, sender=User)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"User {user.username} logged out.")
    print(f"User {user.username} logged out.")
    if user:
        record_history(user, f"用戶 {user.username} 登出了系統")
