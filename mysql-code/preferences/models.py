from django.db import models

class userpreferences(models.Model):
    user_id = models.AutoField(primary_key=True)
    fontsize = models.CharField(max_length=45)
    notificationSettings = models.IntegerField(default=0)  # 對應 tinyint
    autoLogin = models.IntegerField(default=0)  # 對應 tinyint
    authentication = models.BooleanField(default=False)  # 對應 tinyint(1) 作為布林值
