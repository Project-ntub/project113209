from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import pyotp

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, null=False, blank=False, default='0000000000')
    verification_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    expiry_time = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    department_id = models.CharField(max_length=50, blank=True, null=True)
    position_id = models.CharField(max_length=50, blank=True, null=True)
    branch_id = models.CharField(max_length=50, blank=True, null=True)
    module = models.ForeignKey('Module', on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    # 新增的字段
    failed_attempts = models.IntegerField(default=0)  # 密碼錯誤嘗試次數
    is_locked = models.BooleanField(default=False)  # 帳戶是否被鎖定
    last_failed_attempt = models.DateTimeField(null=True, blank=True)  # 記錄最後一次失敗的嘗試時間

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.email

    def generate_otp_secret(self):
        if not self.otp_secret:
            self.otp_secret = pyotp.random_base32()
            self.save()

    def verify_otp(self, otp):
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp)


class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'module'

    def __str__(self):
        return self.name

class RolePermission(models.Model):
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    permission_name = models.CharField(max_length=100)
    can_add = models.BooleanField(default=False)
    can_query = models.BooleanField(default=False)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_print = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    can_maintain = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'role_permission'
        unique_together = ('role', 'permission_name')

    def __str__(self):
        return self.permission_name

class Role(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    users = models.ManyToManyField('User', through='RoleUser', related_name='roles')
    permissions = models.ManyToManyField(RolePermission, related_name='roles')

    class Meta:
        db_table = 'role'

    def __str__(self):
        return self.name

class RoleUser(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'role_users'
        unique_together = ('role', 'user')

class Chart(models.Model):
    CHART_TYPES = [
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        # 添加其他需要的图表类型
    ]

    id = models.AutoField(primary_key=True)
    chart_type = models.CharField(max_length=50, choices=CHART_TYPES)
    chart_name = models.CharField(max_length=255)
    chart_data = models.JSONField()  # 存储图表数据，建议使用 JSON 字段来存储复杂数据
    available = models.BooleanField(default=True)
    create_id = models.ForeignKey('User', related_name='created_charts', on_delete=models.SET_NULL, null=True, blank=True)
    modify_id = models.ForeignKey('User', related_name='modified_charts', on_delete=models.SET_NULL, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='Default Chart Name')

    class Meta:
        db_table = 'charts'

    def __str__(self):
        return self.chart_name

# class DjangoAdminLog(models.Model):
#     action_time = models.DateTimeField(auto_now_add=True, verbose_name="Action Time")
#     object_id = models.TextField(null=True, blank=True, verbose_name="Object ID")
#     object_repr = models.CharField(max_length=200, verbose_name="Object Representation")
#     action_flag = models.PositiveSmallIntegerField(verbose_name="Action Flag")
#     change_message = models.TextField(verbose_name="Change Message")
#     content_type_id = models.IntegerField(null=True, blank=True, verbose_name="Content Type ID")
    
#     # 定义一个外键，指向 Django 内置的 User 模型，用于记录执行操作的用户
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")

#     class Meta:
#         db_table = 'django_admin_log'  # 定义数据库表名称
#         verbose_name = "Django Admin Log"  # 人性化名称
#         verbose_name_plural = "Django Admin Logs"  # 复数形式
#         ordering = ['-action_time']  # 默认按时间倒序排序

#     def __str__(self):
#         return f"{self.object_repr} (Action: {self.action_flag}) at {self.action_time}"

class UserHistory(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='histories')
    action = models.CharField(max_length=500)  # Increased the length for action descriptions
    timestamp = models.DateTimeField(auto_now_add=True)
    device_brand = models.CharField(max_length=255, null=True, blank=True)  # New field for device brand
    device_type = models.CharField(max_length=255, null=True, blank=True)   # New field for device type
    operation_result = models.BooleanField(default=True)  # New field for operation success/failure

    class Meta:
        db_table = 'user_history'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        user_display = self.user.username if self.user else '未知用戶'
        device_brand = self.device_brand if self.device_brand else '未知裝置'
        device_type = self.device_type if self.device_type else '未知類型'
        return f"User {user_display} performed '{self.action}' on {device_brand} ({device_type}) with result {'success' if self.operation_result else 'failure'} at {self.timestamp}"



class UserPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fontsize = models.CharField(max_length=10, default='medium')
    notificationSettings = models.BooleanField(default=True)
    autoLogin = models.BooleanField(default=False)
    authentication = models.BooleanField(default=True)

    class Meta:
        db_table = 'userpreferences'

    def __str__(self):
        return f"{self.user.username}'s Preferences"


#frontend

class Branch(models.Model):
    branch_id = models.AutoField(primary_key=True)  # 主鍵
    branch_name = models.CharField(max_length=100)  # 分店名稱
    address = models.CharField(max_length=255)  # 地址
    manager = models.CharField(max_length=100)  # 經理姓名

    class Meta:
        db_table = 'branches' 
    def __str__(self):
        return self.branch_name

class DataModel(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)  # 关联到分店
    name = models.CharField(max_length=100)  # 数据名称
    value = models.IntegerField()  # 数据值

    class Meta:
        db_table = 'data_model'  # 确保与数据库中的表名一致

    def __str__(self):
        return self.name


class HistoryRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_time = models.DateTimeField(auto_now_add=True)
    action_description = models.TextField()
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.action_description} at {self.action_time}"
    
    
