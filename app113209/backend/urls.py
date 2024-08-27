# app113209/backend/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as backend_views
from . import api_views
from .views import approve_user
router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'modules', api_views.ModuleViewSet)
router.register(r'roles', api_views.RoleViewSet)
router.register(r'role_permissions', api_views.RolePermissionViewSet)

app_name = 'backend'




urlpatterns = [
    path('send_verification_code/', backend_views.send_verification_code_backend, name='send_verification_code_backend'),
    path('verify_code/', backend_views.validate_verification_code_backend, name='verify_code_backend'),
    path('approve_user/<int:user_id>/', approve_user, name='approve_user'),
    path('delete_user/<int:user_id>/', backend_views.delete_user, name='delete_user'),
    path('assign_role_and_module/<int:user_id>/', backend_views.assign_role_and_module, name='assign_role_and_module'),
    path('delete_module/<int:module_id>/', api_views.ModuleViewSet.as_view({'post': 'delete_module'}), name='delete_module'),
    # path('get_preferences/', backend_views.get_preferences, name='get_preferences'),
    # path('update_preference/', backend_views.update_preference, name='update_preference'),
    # path('add_preference/', backend_views.add_preference, name='add_preference'),
    # path('delete_preference/', backend_views.delete_preference, name='delete_preference'),
]

api_urlpatterns = [
    path('', include(router.urls)),
    path('pending-users/', api_views.PendingUserListView.as_view(), name='pending-users-list'),
    path('create_role/', api_views.RoleViewSet.as_view({'post': 'create'}), name='create_role'),
    path('create_module/', api_views.ModuleViewSet.as_view({'post': 'create'}), name='create_module'),
    path('toggle_role_status/<int:pk>/', api_views.RoleViewSet.as_view({'post': 'toggle_status'}), name='toggle_role_status'),
    path('delete_user/<int:pk>/', api_views.UserViewSet.as_view({'post': 'delete'}), name='delete_user'),
    path('delete_role/<int:pk>/', api_views.RoleViewSet.as_view({'post': 'delete'}), name='delete_role'),
    path('delete_module/<int:module_id>/', api_views.ModuleViewSet.as_view({'post': 'delete_module'}), name='delete_module'),
    path('get_modules/', api_views.ModuleViewSet.as_view({'get': 'get_modules'}), name='get_modules'),
    path('get_roles_by_module/<int:pk>/', api_views.RoleViewSet.as_view({'get': 'get_roles_by_module'}), name='get_roles_by_module'),
    path('assign_role_and_module/<int:user_id>/', api_views.UserViewSet.as_view({'post': 'assign_role_and_module'}), name='assign_role_and_module'),
    path('get_role_users/', api_views.UserViewSet.as_view({'get': 'get_role_users'}), name='get_role_users'),
    path('roles/', api_views.RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', api_views.RoleRetrieveUpdateDestroyView.as_view(), name='role-retrieve-update-destroy'),
    path('role_permissions/', api_views.RolePermissionListCreateView.as_view(), name='role-permission-list-create'),
    path('role_permissions/<int:pk>/', api_views.RolePermissionRetrieveUpdateDestroyView.as_view(), name='role-permission-retrieve-update-destroy'),
    path('modules/', api_views.ModuleListCreateView.as_view(), name='module-list-create'),
    path('modules/<int:pk>/', api_views.ModuleRetrieveUpdateDestroyView.as_view(), name='module-retrieve-update-destroy'),
    path('profile/', api_views.UserProfileView.as_view(), name='user-profile'),
    path('user_history/', api_views.UserHistoryListView.as_view(), name='user-history-list'),
    path('user_preferences/', api_views.UserPreferenceView.as_view(), name='user_preferences'),
]

urlpatterns += [
    path('api/', include(api_urlpatterns)),
]

