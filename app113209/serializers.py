from rest_framework import serializers
from .models import User, Module, Role, RolePermission

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

class RoleSerializer(serializers.ModelSerializer):
    module = ModuleSerializer()  # 使用嵌套的 ModuleSerializer 来显示模块详细信息
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())  # 假设 Role 和 User 是多对多关系

    class Meta:
        model = Role
        fields = ['id', 'name', 'is_active', 'module', 'users']
        extra_kwargs = {
            'name': {'required': True},
            'module': {'required': True},
            'users': {'required': True}
        }

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)  # 将 read_only=True 设为避免与嵌套序列化器冲突
    module = ModuleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'module', 'phone', 'is_verified', 'is_approved', 'department_id', 'position_id', 'branch_id', 'module', 'gender', 'is_staff', 'is_active', 'is_deleted', 'date_joined')

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = ('id', 'role', 'permission_name', 'can_add', 'can_query', 'can_view', 'can_edit', 'can_delete', 'can_print', 'can_export', 'can_maintain', 'is_deleted')
        extra_kwargs = {
            'role': {'required': True},
            'permission_name': {'required': True}
        }

