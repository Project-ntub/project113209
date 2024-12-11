# app113209\backend\api_urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views
# from .api_views import get_revenue_data, get_sales_data, get_stock_data
router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'modules', api_views.ModuleViewSet)
router.register(r'roles', api_views.RoleViewSet)
router.register(r'role_permissions', api_views.RolePermissionViewSet)
router.register(r'pending-users', api_views.PendingUserViewSet, basename='pending-user')
router.register(r'permissions', api_views.UserPermissionViewSet, basename='user-permissions')
router.register(r'charts', api_views.ChartConfigurationViewSet, basename='chart-configuration')
router.register(r'user_preferences', api_views.UserPreferencesViewSet, basename='user_preferences')

urlpatterns = [
    path('', include(router.urls)),
    # path('token/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', api_views.logout_view, name='logout'),
    path('pending-users/', api_views.PendingUserViewSet.as_view({'get': 'list'}), name='pending-users-list'),
    path('approve-user/<int:pk>/', api_views.PendingUserViewSet.as_view({'post': 'approve_user'}), name='approve-user'),
    path('create_role/', api_views.RoleViewSet.as_view({'post': 'create'}), name='create_role'),
    path('create_module/', api_views.ModuleViewSet.as_view({'post': 'create'}), name='create_module'),
    path('toggle_role_status/<int:pk>/', api_views.RoleViewSet.as_view({'post': 'toggle_status'}), name='toggle_role_status'),
    path('delete_user/<int:pk>/', api_views.UserViewSet.as_view({'delete': 'destroy'}), name='delete_user'),
    path('delete_role/<int:pk>/', api_views.RoleViewSet.as_view({'post': 'delete'}), name='delete_role'),
    path('delete_module/<int:module_id>/', api_views.ModuleViewSet.as_view({'post': 'delete_module'}), name='delete_module'),
    path('get_modules/', api_views.ModuleViewSet.as_view({'get': 'get_modules'}), name='get_modules'),
    path('get_roles_by_module/<int:pk>/', api_views.RoleViewSet.as_view({'get': 'get_roles_by_module'}), name='get_roles_by_module'),
    path('assign_role_and_module/<int:pk>/', api_views.UserViewSet.as_view({'post': 'assign_role_and_module'}), name='assign_role_and_module'),
    path('get_role_users/', api_views.UserViewSet.as_view({'get': 'get_role_users'}), name='get_role_users'),
    
    # 角色和模塊管理
    path('roles/', api_views.RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', api_views.RoleRetrieveUpdateDestroyView.as_view(), name='role-retrieve-update-destroy'),
    path('role_permissions/', api_views.RolePermissionListCreateView.as_view(), name='role-permission-list-create'),
    path('role_permissions/<int:pk>/', api_views.RolePermissionRetrieveUpdateDestroyView.as_view(), name='role-permission-retrieve-update-destroy'),
    path('modules/', api_views.ModuleListCreateView.as_view(), name='module-list-create'),
    path('modules/<int:pk>/', api_views.ModuleRetrieveUpdateDestroyView.as_view(), name='module-retrieve-update-destroy'),
    
    # 與用戶相關的視圖
    path('profile/', api_views.UserProfileView.as_view(), name='user-profile'),
    path('user_history/', api_views.UserHistoryListView.as_view(), name='user-history-list'),
    # path('approve-user/<int:pk>/', api_views.PendingUserViewSet.as_view({'post': 'approve_user'}), name='approve-user'),
    path('departments/', api_views.UserViewSet.as_view({'get': 'get_departments'}), name='get_departments'),
    path('get_positions_by_department/<str:department_id>/', api_views.UserViewSet.as_view({'get': 'get_positions_by_department'}), name='get_positions_by_department'),

    # 圖表與數據 API
    path('data-sources/', api_views.get_data_sources, name='get_data_sources'),
    path('table-fields/<str:table_name>/', api_views.get_table_fields, name='get_table_fields'),
    path('charts/<int:id>/', api_views.ChartConfigurationViewSet.as_view({'get': 'retrieve'}), name='charts-retrieve'),
    path('chart-data/<str:table_name>/', api_views.get_chart_data, name='get_chart_data'),
    path('create-chart/', api_views.ChartConfigurationViewSet.as_view({'post': 'create_chart_action'}), name='create_chart'),
    path('update-chart/<int:pk>/', api_views.ChartConfigurationViewSet.as_view({'post': 'update_chart'}), name='update_chart'),
    path('delete-chart/<int:pk>/', api_views.ChartConfigurationViewSet.as_view({'post': 'delete_chart'}), name='delete_chart'),
    path('get-chart-configurations/', api_views.get_chart_configuration, name='get_chart_configurations'),
    path('dynamic-chart-data/', api_views.dynamic_chart_data, name='dynamic_chart_data'),
    path('table-fields-metadata/<str:table_name>/', api_views.get_table_fields_metadata, name='get_table_fields_metadata'),
    path('get-options/<str:related_model>/', api_views.get_options, name='get_options'),


    # 圖表數據（更正名稱以避免衝突）
    # path('sales-chart-data/', api_views.SalesDataAPIView.as_view(), name='sales-chart-data'),
    # path('revenue-chart-data/', api_views.RevenueDataAPIView.as_view(), name='revenue-chart-data'),
    # path('inventory-chart-data/', api_views.InventoryDataAPIView.as_view(), name='inventory-chart-data'),
    # path('sales-volume-chart-data/', api_views.SalesVolumeChartDataAPIView.as_view(), name='sales-volume-chart-data'),
    # path('store-comparison-chart-data/', api_views.StoreComparisonChartDataAPIView.as_view(), name='store-comparison-chart-data'),
    # path('product-sales-pie-chart-data/', api_views.ProductSalesPieChartAPIView.as_view(), name='product-sales-pie-chart-data'),


    # 數據端點
    path('inventory/', api_views.InventoryDataAPIView.as_view(), name='inventory-data'),
    path('sales-data/', api_views.SalesDataAPIView.as_view(), name='sales-data'),
    path('revenue-data/', api_views.RevenueDataAPIView.as_view(), name='revenue-data'),

    # 圖片生成
    # path('generate-chart-image/', api_views.generate_chart_image, name='generate-chart-image')

    # 匯出數據 API
    path('export-data/', api_views.export_data, name='export-data'),
    path('export-data-csv/', api_views.export_to_csv, name='export-data-csv'),
    path('export-data-excel/', api_views.export_to_excel, name='export-data-excel'),
    path('export-data-pdf/', api_views.export_to_pdf, name='export-data-pdf'),

    path('save-layout/', api_views.save_layout, name='save_layout'),
    path('get-layout/', api_views.get_layout, name='get_layout'),

    # 另一個資料庫的圖表數據

    path('dashboard/revenue/', api_views.get_revenue_data, name='get_revenue_data'),
    path('dashboard/sales/', api_views.get_sales_data, name='get_sales_data'),
    path('dashboard/stock/', api_views.get_stock_data, name='get_stock_data'),
    path('dashboard/card-data/', api_views.calculate_card_data, name='calculate_card_data'),

    path('get-product-names/', api_views.get_product_names, name='get_product_names'),
    path('get-store-names/', api_views.get_store_names, name='get_store_names'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
