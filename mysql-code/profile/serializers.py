from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'department_id', 'position_id', 'branch_id', 'gender', 'font_size', 'notifications_enabled', 'auto_login_enabled', 'authentication_enabled', 'is_verified', 'is_approved', 'created_at']  # 包含您需要的字段

    def update(self, instance, validated_data):
        # 更新 CustomUser 模型中的字段
        user_data = validated_data.pop('user', None)
        instance = super().update(instance, validated_data)

        # 如果有需要，可以更新其他字段
        if user_data:
            instance.username = user_data.get('username', instance.username)
            instance.email = user_data.get('email', instance.email)
            instance.save()

        return instance
