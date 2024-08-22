from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction  # 導入 transaction
from .models import CustomUser  # 使用 CustomUser 模型
from .serializers import CustomUserSerializer  # 使用對應的序列化器

class UserProfileView(APIView):
    """
    處理用戶資料的 APIView。支持 GET 和 POST 請求。
    """

    def get(self, request):
        """
        處理 GET 請求，返回當前用戶的資料。
        """
        try:
            user = CustomUser.objects.get(id=request.user.id)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        處理 POST 請求，更新當前用戶的資料。
        使用 transaction.atomic 確保資料庫操作的一致性。
        """
        try:
            with transaction.atomic():
                user = CustomUser.objects.get(id=request.user.id)
                serializer = CustomUserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': 'Profile updated successfully'})
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
