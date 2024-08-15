# app113209/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import ActionLog, User
from .serializers import ActionLogSerializer, UserSerializer

class ActionLogViewSet(viewsets.ModelViewSet):
    queryset = ActionLog.objects.all()
    serializer_class = ActionLogSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            ActionLog.objects.create(
                user=request.user,
                action_type='Create',
                details=f"Created user: {response.data['username']}"
            )
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            ActionLog.objects.create(
                user=request.user,
                action_type='Update',
                details=f"Updated user: {response.data['username']}"
            )
        return response

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            ActionLog.objects.create(
                user=request.user,
                action_type='Delete',
                details=f"Deleted user: {user.username}"
            )
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        ActionLog.objects.create(
            user=request.user,
            action_type='Query',
            details=f"Queried user list"
        )
        return response
