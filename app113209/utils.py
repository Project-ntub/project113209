# app113209\utils.py
import logging
from app113209.models import UserHistory, User
from django.utils import timezone

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
