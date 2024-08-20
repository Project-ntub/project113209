from django.urls import path
from .views import UserProfileView  # 確保這裡的引用正確

urlpatterns = [
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
]
