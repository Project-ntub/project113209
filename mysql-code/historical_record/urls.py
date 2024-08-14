# app113209/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActionLogViewSet, UserViewSet

router = DefaultRouter()
router.register(r'action_logs', ActionLogViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
