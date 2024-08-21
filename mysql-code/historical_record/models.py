from django.db import models
from django.contrib.auth.models import User  # 导入 Django 内置的 User 模型

class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField(auto_now_add=True, verbose_name="Action Time")
    object_id = models.TextField(null=True, blank=True, verbose_name="Object ID")
    object_repr = models.CharField(max_length=200, verbose_name="Object Representation")
    action_flag = models.PositiveSmallIntegerField(verbose_name="Action Flag")
    change_message = models.TextField(verbose_name="Change Message")
    content_type_id = models.IntegerField(null=True, blank=True, verbose_name="Content Type ID")
    
    # 定义一个外键，指向 Django 内置的 User 模型，用于记录执行操作的用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")

    class Meta:
        db_table = 'django_admin_log'  # 定义数据库表名称
        verbose_name = "Django Admin Log"  # 人性化名称
        verbose_name_plural = "Django Admin Logs"  # 复数形式
        ordering = ['-action_time']  # 默认按时间倒序排序

    def __str__(self):
        return f"{self.object_repr} (Action: {self.action_flag}) at {self.action_time}"
