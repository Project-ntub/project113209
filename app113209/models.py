from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import models
import pyotp
# app113209/frontend/models.py
from django.db import models

class CalendarEvent(models.Model):
    title = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



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
    email_verified = models.BooleanField(default=False)  # 新增的欄位

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
    permission_name = models.CharField(max_length=100, unique=True)    
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
        # unique_together = ('role', 'permission_name')

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


User = get_user_model()

class Chart(models.Model):
    CHART_TYPES = [
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('scatter', 'Scatter Plot'),  # 散點圖
        ('area', 'Area Chart'),  # 區域圖
        ('histogram', 'Histogram'),  # 直方圖
        ('heatmap', 'Heatmap'),  # 熱力圖
        {'horizontal_bar', 'Horizontal Bar Chart'},
        {'multi_line', 'Multi-line Chart'},
        {'combo', 'Combination Chart'},
        ('bubble', 'Bubble Chart'),  # 泡泡圖
        ('donut', 'Donut Chart'),  # 甜甜圈圖
        ('radar', 'Radar Chart'),  # 雷達圖
        ('gauge', 'Gauge Chart'),  # 儀表圖
        ('funnel', 'Funnel Chart'),  # 漏斗圖
        ('treemap', 'Treemap'),  # 矩形樹圖
        ('waterfall', 'Waterfall Chart'),  # 瀑布圖
        ('box', 'Box Plot'),  # 箱形圖
        # 可以根據需要添加更多的圖表類型
    ]

    id = models.AutoField(primary_key=True, default=1)
    chart_type = models.CharField(max_length=50, choices=CHART_TYPES)
    chart_name = models.CharField(max_length=255)
    chart_data = models.JSONField()  # 存储图表数据，建议使用 JSON 字段来存储复杂数据
    is_visible = models.BooleanField(default=True)  # 更明确的字段名
    created_by = models.ForeignKey(User, related_name='created_charts', on_delete=models.SET_NULL, null=True, blank=True)
    modified_by = models.ForeignKey(User, related_name='modified_charts', on_delete=models.SET_NULL, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, null=True, blank=True)  # 设置为可为空
    name = models.CharField(max_length=255)  # 去除默认值，确保每个图表都有明确名称

    class Meta:
        db_table = 'charts'

    def __str__(self):
        return self.chart_name

class ChartConfiguration(models.Model):
    CHART_TYPES = [
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('heatmap', 'Heatmap'),  # 新增熱力圖
        ('horizontal_bar', 'Horizontal Bar Chart'),  # 新增橫條圖
        ('multi_line', 'Multi-line Chart'),  # 新增多線折線圖
        ('combo', 'Combination Chart'),  # 新增組合式圖表
        # ...可以根據需要添加更多的圖表類型
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    chart_type = models.CharField(max_length=50)
    data_source = models.CharField(max_length=100)
    x_axis_field = models.CharField(max_length=100)
    y_axis_field = models.CharField(max_length=100)
    y_axis_fields = models.JSONField(blank=True, null=True)  # 新增，用於多線折線圖
    filter_conditions = models.JSONField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)  # 用來標記是否已刪除/隱藏
    ordering = models.JSONField(blank=True, null=True)  # 新增，用於排序
    limit = models.IntegerField(blank=True, null=True)  # 新增，用於限制資料筆數
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    color = models.JSONField(default=dict)  # 存儲顏色的 HEX 值


    def __str__(self):
        return self.name

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


class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fontsize = models.CharField(max_length=10, choices=[('small', '小'), ('medium', '中'), ('large', '大')], default='medium')
    notificationSettings = models.BooleanField(default=False)
    authentication = models.BooleanField(default=False)

    class Meta:
        db_table = 'userpreferences'

    def __str__(self):
        return f"{self.user.username}'s Preferences"

@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)
    

#frontend

class Branch(models.Model):
    branch_id = models.CharField(max_length=50, primary_key=True)
    branch_name = models.CharField(max_length=45, unique=True)
    address = models.CharField(max_length=45, null=True, blank=True)
    manager = models.CharField(max_length=45, unique=True)

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
    

#圖表資料
class TEST_Stores(models.Model):
    store_id = models.AutoField(primary_key=True, default=1)
    store_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TEST_Stores'

    def __str__(self):
        return self.store_name

# 測試用產品模型
class TEST_Products(models.Model):
    product_id = models.CharField(max_length=50, primary_key=True)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 修改為 DecimalField
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'TEST_Products'

    def __str__(self):
        return self.product_name

# 測試用銷售模型
class TEST_Sales(models.Model):
    sale_id = models.CharField(max_length=50, primary_key=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # 修改為 DecimalField
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)  # 修改為 DecimalField
    sale_date = models.DateTimeField()  # 修改為 DateTimeField 或 DateField
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(TEST_Products, on_delete=models.CASCADE, null=True, db_column='product_id')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, db_column='branch_id')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 修改為 DecimalField

    class Meta:
        db_table = 'TEST_Sales'

    def __str__(self):
        branch_name = self.branch.branch_name if self.branch else 'N/A'
        product_name = self.product.product_name if self.product else 'N/A'
        return f"Sale ID: {self.sale_id}, Branch: {branch_name}, Product: {product_name}"


class TEST_Inventory(models.Model):
    id = models.AutoField(primary_key=True)  # 自動遞增主鍵
    product_name = models.CharField(max_length=200, null=True, blank=True)
    warehouse_id = models.CharField(max_length=50)  # NOT NULL, 預設 null=False
    warehouse_name = models.CharField(max_length=200, null=True, blank=True)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(
        TEST_Products,
        on_delete=models.CASCADE,
        db_column='product_id',  # 指定資料庫中的欄位名稱
        related_name='inventories'  # 可選，便於反向查詢
    )
    unit = models.CharField(max_length=50, null=True, blank=True)  # 新增的 unit 欄位

    class Meta:
        db_table = 'TEST_Inventory'
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return f"Inventory {self.id} - {self.product_name} in {self.warehouse_name}"

class TEST_Revenue(models.Model):
    id = models.AutoField(primary_key=True)  # 新增自動遞增主鍵
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, db_column='branch_id')
    branch_name = models.CharField(max_length=100, null=True)
    product = models.ForeignKey(TEST_Products, on_delete=models.CASCADE, null=True, db_column='product_id')
    revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    net_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    cost_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    final_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'TEST_Revenue'

    def __str__(self):
        return f"Revenue {self.id} for Branch {self.branch_name} - Product {self.product.product_id}"


# 另外一個資料庫的圖表
class SalesData(models.Model):
    sale_date = models.DateField()
    branch_name = models.CharField(max_length=100)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)

class StockData(models.Model):
    product_name = models.CharField(max_length=100)
    stock_quantity = models.IntegerField()