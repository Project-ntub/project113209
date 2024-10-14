# app113209\utils.py
import logging
from app113209.models import UserHistory, User, RolePermission
from django.utils import timezone
from django.utils.text import slugify


logger = logging.getLogger(__name__)


def record_history(user, action_desc):
    try:
        # 在創建歷史記錄之前檢查用戶是否存在
        if User.objects.filter(id=user.id).exists():
            UserHistory.objects.create(
                user_id=user.id,
                action=action_desc,
                timestamp=timezone.now()
            )
            logger.info(f"History record created for user {user.username} with action: {action_desc}")
        else:
            logger.warning(f"User with ID {user.id} does not exist.")
    except Exception as e:
        logger.error(f"Error creating history record for user {user.id}: {e}")

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