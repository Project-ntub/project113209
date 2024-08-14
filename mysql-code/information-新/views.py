# app113209/views.py
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

# 視圖集：處理用戶的新增、刪除、修改、查詢
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # 查詢功能
    serializer_class = UserSerializer

    # 新增功能：默認處理 POST 請求
    # 刪除功能：默認處理 DELETE 請求
    # 修改功能：默認處理 PUT/PATCH 請求
    # 查詢功能：默認處理 GET 請求
