# app113209\backend\api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'modules', api_views.ModuleViewSet)
router.register(r'roles', api_views.RoleViewSet)
router.register(r'role_permissions', api_views.RolePermissionViewSet)
router.register(r'pending-users', api_views.PendingUserViewSet, basename='pending-user')
router.register(r'user_preferences', api_views.UserPreferencesViewSet, basename='user_preferences')


urlpatterns = [
    path('', include(router.urls)),
    #path('pending-users/', api_views.PendingUserViewSet.as_view(), name='pending-users-list'),
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
    path('user_preferences/', api_views.UserPreferencesViewSet.as_view({'get': 'list', 'post': 'create'}), name='user_preferences'),
    path('approve-user/<int:pk>/', api_views.PendingUserViewSet.as_view({'post': 'approve_user'}), name='approve-user'),
    path('departments/', api_views.UserViewSet.as_view({'get': 'get_departments'}), name='get_departments'),  # 正確設置actions參數
    path('get_positions_by_department/<str:department_id>/', api_views.UserViewSet.as_view({'get': 'get_positions_by_department'}), name='get_positions_by_department'),  # 正確設置actions參數
    path('data-sources/', api_views.get_data_sources, name='get_data_sources'),
    path('table-fields/<str:table_name>/', api_views.get_table_fields, name='get_table_fields'),
    path('charts/', api_views.ChartConfigurationViewSet.as_view({'get': 'list'}), name='charts-list'),
    path('inventory/', api_views.InventoryDataAPIView.as_view(), name='inventory-data'),
    path('sales-data/', api_views.SalesDataAPIView.as_view(), name='sales-data'),
    path('revenue/', api_views.RevenueDataAPIView.as_view(), name='sales-data'),
    path('revenue-chart-data/', api_views.revenue_chart_data, name='revenue_chart_data'),
    path('sales-chart-data/', api_views.sales_chart_data, name='sales_chart_data'),
    path('inventory-chart-data/', api_views.inventory_chart_data, name='inventory_chart_data'),
    path('chart-data/', api_views.ChartDataAPIView.as_view(), name='chart-data'),
    path('create-chart/', api_views.ChartConfigurationViewSet.as_view({'post': 'create_chart'}), name='create_chart'),
    path('update-chart/<int:pk>/', api_views.ChartConfigurationViewSet.as_view({'post': 'update_chart'}), name='update_chart'),
    # path('api/branches/', api_views.get_branches, name='get_branches'),

]
