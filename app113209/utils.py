# utils.py (新建這個檔案以儲存公共的輔助函數)

from app113209.models import UserHistory, User
from django.utils import timezone

def record_history(user, action_desc):
    try:
        # 在創建歷史記錄之前檢查用戶是否存在
        if User.objects.filter(id=user.id).exists():
            UserHistory.objects.create(
                user_id=user.id,
                action=action_desc,
                timestamp=timezone.now()
            )
        else:
            print(f"ID 為 {user.id} 的用戶不存在。")
    except User.DoesNotExist:
        print(f"ID 為 {user.id} 的用戶不存在。")

