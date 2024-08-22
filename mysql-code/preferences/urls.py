from django.urls import path
from .views import get_preferences, update_preference, add_preference, delete_preference, query_preferences

urlpatterns = [
    path('get_preferences/', get_preferences, name='get_preferences'),
    path('update_preference/', update_preference, name='update_preference'),
    path('add_preference/', add_preference, name='add_preference'),
    path('delete_preference/', delete_preference, name='delete_preference'),
    path('query_preferences/', query_preferences, name='query_preferences'),
]
