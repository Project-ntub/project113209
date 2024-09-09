# app113209/backend/urls.py
from django.urls import path, include
from . import views as backend_views
from . import api_views


app_name = 'backend'


urlpatterns = [
    path('send_verification_code/', backend_views.send_verification_code_backend, name='send_verification_code_backend'),
    path('verify_code/', backend_views.validate_verification_code_backend, name='verify_code_backend'),
    path('delete_user/<int:user_id>/', backend_views.delete_user, name='delete_user'),
    path('assign_role_and_module/<int:user_id>/', backend_views.assign_role_and_module, name='assign_role_and_module'),
    path('delete_module/<int:module_id>/', api_views.ModuleViewSet.as_view({'post': 'delete_module'}), name='delete_module'),
    # path('api/branches/', backend_views.get_branches, name='get_branches'),
    # path('get_preferences/', backend_views.get_preferences, name='get_preferences'),
    # path('update_preference/', backend_views.update_preference, name='update_preference'),
    # path('add_preference/', backend_views.add_preference, name='add_preference'),
    # path('delete_preference/', backend_views.delete_preference, name='delete_preference'),
]

