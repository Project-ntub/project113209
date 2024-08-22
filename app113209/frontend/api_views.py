from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app113209.models import User
from app113209.serializers import UserSerializer

class CurrentUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# app113209/frontend/api_views.py

from app113209.models import Branch

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def branch_list(request):
    branches = Branch.objects.all().values('branch_id', 'branch_name', 'address', 'manager')
    data = list(branches)
    return Response(data, status=status.HTTP_200_OK)
