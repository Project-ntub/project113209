import json
from rest_framework import serializers
from .models import User, Module, Role, RoleUser, RolePermission, UserHistory, ChartConfiguration, TEST_Sales, UserPreferences, Branch, TEST_Inventory, TEST_Revenue, UserLayout

from rest_framework import serializers
from app113209.models import CalendarEvent

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = ['id', 'title', 'start', 'end', 'description', 'created_at', 'updated_at']

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = ('id', 'role', 'permission_name', 'can_add', 'can_query', 'can_view', 'can_edit', 'can_delete', 'can_print', 'can_export', 'can_maintain', 'is_deleted')
        extra_kwargs = {
            'role': {'required': True},
            'permission_name': {'required': True}
        }

class ModuleSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ('id', 'name', 'user_count', 'is_deleted')
        extra_kwargs = {
            'name': {'required': True},
        }

    def get_user_count(self, obj):
        return RoleUser.objects.filter(
                    role__module=obj,
                    role__is_active=True,
                    role__is_deleted=False,
                    # user__is_active=True,  # 確保用戶本身也是活躍的
                    user__is_deleted=False  # 確保用戶本身未被刪除
                ).distinct().count()

class SimpleRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    module = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'roles', 'module', 'phone', 'is_verified', 'is_approved', 'department_id', 'position_id', 'branch_id', 'gender', 'is_staff', 'is_active', 'is_deleted', 'date_joined', 'last_login')

    def get_roles(self, obj):
        roles = Role.objects.filter(roleuser__user=obj, is_deleted=False)
        return SimpleRoleSerializer(roles, many=True).data

    def get_module(self, obj):
        role = Role.objects.filter(roleuser__user=obj, is_deleted=False).first()
        if role:
            return ModuleSerializer(role.module).data
        return None

class RoleSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all())
    module_name = serializers.CharField(source='module.name', read_only=True)
    users = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_users(self, obj):
        # 如果需要返回角色相關的用戶，可以返回用戶的基本信息，而不是完整的 UserSerializer
        users = obj.users.all()
        return [{'id': user.id, 'username': user.username} for user in users]


class UserHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserHistory
        fields = ['id', 'user', 'action', 'timestamp', 'device_brand', 'device_type', 'operation_result']


class ChartConfigurationSerializer(serializers.ModelSerializer):
    # 讀取時使用駝峰命名
    chartType = serializers.CharField(source='chart_type', read_only=True)
    dataSource = serializers.CharField(source='data_source', read_only=True)
    xAxisField = serializers.CharField(source='x_axis_field', read_only=True)
    yAxisField = serializers.CharField(source='y_axis_field', read_only=True)
    yAxisFields = serializers.ListField(source='y_axis_fields', read_only=True)

    # 寫入時接受蛇形命名
    chart_type = serializers.CharField(write_only=True)
    data_source = serializers.CharField(write_only=True)
    x_axis_field = serializers.CharField(write_only=True)
    y_axis_field = serializers.CharField(write_only=True, required=False, allow_blank=True)
    y_axis_fields = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)


    color = serializers.JSONField(required=False)


    class Meta:
        model = ChartConfiguration
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 確保 filter_conditions 正確地對應為 filterConditions
        data['filterConditions'] = data.pop('filterConditions', {})
        return data

    def to_internal_value(self, data):
        # 允許前端使用駝峰命名或蛇形命名
        data['chart_type'] = data.get('chartType', data.get('chart_type'))
        data['data_source'] = data.get('dataSource', data.get('data_source'))
        data['x_axis_field'] = data.get('xAxisField', data.get('x_axis_field'))
        data['y_axis_field'] = data.get('yAxisField', data.get('y_axis_field'))
        data['y_axis_fields'] = data.get('yAxisFields', data.get('y_axis_fields'))
        data['filter_conditions'] = data.get('filterConditions', data.get('filter_conditions'))
        return super().to_internal_value(data)

    def validate(self, data):
        # 確保圖表名稱不為空
        if not data.get('name'):
            raise serializers.ValidationError({'name': '此欄位不能為空.'})  # 修正 'n ame' 為 'name'
        
        # 確保數據來源不為空
        if not data.get('data_source'):
            raise serializers.ValidationError({'data_source': '此欄位不能為空.'})
        
        # 確保 x 軸資料欄位不為空
        if not data.get('x_axis_field'):
            raise serializers.ValidationError({'x_axis_field': 'X 軸資料欄位不能為空.'})
        
        chart_type = data.get('chart_type')

        if chart_type in ['multi_line', 'combo']:
            # 對於 multi_line 和 combo 圖表，驗證 y_axis_fields
            y_axis_fields = data.get('y_axis_fields')
            if not y_axis_fields or len(y_axis_fields) < 2:
                raise serializers.ValidationError({'y_axis_fields': '請至少選擇兩個 Y 軸欄位。'})
        else:
            # 對於其他圖表類型，驗證 y_axis_field
            if not data.get('y_axis_field'):
                raise serializers.ValidationError({'y_axis_field': 'Y 軸資料欄位不能為空。'})
        
        # 確保過濾條件是字典而不是字符串
        if 'filter_conditions' in data and data['filter_conditions']:
            if isinstance(data['filter_conditions'], str):
                try:
                    data['filter_conditions'] = json.loads(data['filter_conditions'])
                except json.JSONDecodeError:
                    raise serializers.ValidationError("Filter conditions must be valid JSON.")
        return data
    
class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ['id', 'user_id', 'fontsize', 'notificationSettings', 'authentication']


# 圖表權限

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['branch_id', 'branch_name']

class SalesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TEST_Sales
        fields = '__all__'  # 或者指定要序列化的字段

class InventoryDataSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.store_name', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)

    class Meta:
        model = TEST_Inventory
        fields = ['inventory_id', 'store', 'store_name', 'product', 'product_name', 'stock_quantity', 'last_updated']

class RevenueDataSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.store_name', read_only=True)

    class Meta:
        model = TEST_Revenue
        fields = ['revenue_id', 'store', 'store_name', 'total_revenue', 'revenue_date', 'created_at']  

class UserLayoutSerializer(serializers.ModelSerializer):
    layout = serializers.JSONField(required=False)
    updated_at = serializers.DateTimeField(read_only=True)  # 確保更新時間是只讀的
    
    class Meta:
        model = UserLayout
        fields = ['layout', 'updated_at']
        
    def validate_layout(self, value):
        """驗證佈局數據的格式和內容"""
        is_valid, error_message = validate_layout_data(value)
        if not is_valid:
            raise serializers.ValidationError(error_message)
            
        # 額外驗證：確保所有數值在合理範圍內
        for item in value:
            if item['x'] < 0 or item['y'] < 0:
                raise serializers.ValidationError("座標值不能為負數")
            if item['w'] < 1 or item['h'] < 1:
                raise serializers.ValidationError("寬度和高度必須大於0")
                
        return value