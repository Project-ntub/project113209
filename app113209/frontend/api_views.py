# app113209\frontend\api_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app113209.models import User, UserHistory
from app113209.serializers import UserSerializer



# app113209/frontend/api_views.py
from rest_framework import viewsets
from app113209.models import CalendarEvent
from app113209.serializers import CalendarEventSerializer

# 定義 CalendarEvent 的 CRUD API
class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer

class CurrentUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # 獲取當前用戶的個人資訊
    def list(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # 更新個人資訊
    def update(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()

            # 當資料成功更新後，記錄歷史紀錄
            UserHistory.objects.create(
                user=user,
                action='更新個人資訊',
                operation_result=True  # 操作成功
            )

            return Response(serializer.data)

        # 若更新失敗，僅返回錯誤訊息，不記錄歷史紀錄
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# app113209/frontend/api_views.py

from app113209.models import Branch

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def branch_list(request):
    branches = Branch.objects.all().values('branch_id', 'branch_name', 'address', 'manager')
    data = list(branches)
    return Response(data, status=status.HTTP_200_OK)
