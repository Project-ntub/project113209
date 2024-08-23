from django.urls import path
from . import views

urlpatterns = [
    path('get_preferences/', views.get_preferences, name='get_preferences'),
    path('update_preference/', views.update_preference, name='update_preference'),
    path('add_preference/', views.add_preference, name='add_preference'),
    path('delete_preference/', views.delete_preference, name='delete_preference'),
]
