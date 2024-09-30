from rest_framework import serializers
from .models import User, Module, Role, RolePermission, UserHistory, ChartConfiguration, TEST_Sales, UserPreferences, Branch, TEST_Inventory, TEST_Revenue


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
        return User.objects.filter(roles__module=obj, is_active=True).count()

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
        fields = ['id', 'name', 'is_active', 'module', 'module_name', 'users']

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
    class Meta:
        model = ChartConfiguration
        fields = ['id', 'user', 'name', 'chart_type', 'data_source', 'x_axis_field', 'y_axis_field', 'filter_conditions', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        if not data.get('name'):
            raise serializers.ValidationError({'name': 'This field may not be blank.'})
        if not data.get('data_source'):
            raise serializers.ValidationError({'data_source': 'This field is required.'})
        if not data.get('x_axis_field'):
            raise serializers.ValidationError({'x_axis_field': 'This field is required.'})
        if not data.get('y_axis_field'):
            raise serializers.ValidationError({'y_axis_field': 'This field is required.'})

        # 確保過濾條件是字典而不是字符串
        if isinstance(data.get('filter_conditions'), str):
            try:
                data['filter_conditions'] = json.loads(data['filter_conditions'])
            except ValueError:
                raise serializers.ValidationError({'filter_conditions': 'Invalid JSON format'})
        
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

        