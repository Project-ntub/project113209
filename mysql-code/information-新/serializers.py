# app113209/serializers.py
from rest_framework import serializers
from .models import User

# 序列化器：將 User 模型轉換為 JSON 格式
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
