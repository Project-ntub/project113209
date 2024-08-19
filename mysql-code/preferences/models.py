from django.db import models

class UserPreference(models.Model):
    user_id = models.AutoField(primary_key=True)  # 主鍵，自動增長
    fontsize = models.CharField(max_length=45)
    notificationSettings = models.CharField(max_length=45)
    autoLogin = models.CharField(max_length=45)

    def __str__(self):
        return f"UserPreference(user_id={self.user_id}, fontsize={self.fontsize})"
