# app113209/frontend/api_urls.py
from django.urls import path
from .api_views import CurrentUserViewSet, branch_list

urlpatterns = [
    path('profile/', CurrentUserViewSet.as_view({'get': 'list', 'put': 'update'}), name='profile'),
    path('branches/', branch_list, name='get_branches')
]
