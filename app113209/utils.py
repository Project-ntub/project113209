# app113209\utils.py
import logging
from app113209.models import UserHistory, User, RolePermission
from django.utils import timezone
from django.utils.text import slugify


logger = logging.getLogger(__name__)


def record_history(user, action, device_brand=None, device_type=None, operation_result=True):
    try:
        UserHistory.objects.create(
            user=user,
            action=action,
            device_brand=device_brand,
            device_type=device_type,
            operation_result=operation_result,
        )
        logger.debug(f"Recorded history for user {user.email}: {action}")
    except Exception as e:
        logger.error(f"Error recording history for user {user.email}: {e}")

def update_permission_name(old_name, new_name):
    """
    更新 RolePermission 中的 permission_name 從舊名稱到新名稱。
    
    Args:
        old_name (str): 圖表的舊名稱。
        new_name (str): 圖表的新名稱。
    """
    old_permission_name = slugify(f"chart_{old_name}")
    new_permission_name = slugify(f"chart_{new_name}")
    RolePermission.objects.filter(permission_name=old_permission_name).update(permission_name=new_permission_name)