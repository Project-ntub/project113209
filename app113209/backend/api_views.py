# C:\Users\user\OneDrive\桌面\project113209\app113209\backend\api_views.py
import json
import logging
import plotly.graph_objs as go
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import F  # 添加这行
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from app113209.models import (User, Module, Role, RolePermission, UserHistory, 
                             UserPreferences, ChartConfiguration, TEST_Inventory, 
                              TEST_Revenue, TEST_Sales, TEST_Products, TEST_Stores)
from app113209.serializers import (UserSerializer, ModuleSerializer, RoleSerializer, 
                                   RolePermissionSerializer, UserHistorySerializer, 
                                   ChartConfigurationSerializer, SalesDataSerializer, UserPreferencesSerializer)
from app113209.utils import record_history
from plotly.graph_objs import Bar, Scatter, Pie


logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False, is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def assign_role_and_module(self, request, pk=None):
        user = self.get_object()
        module_id = request.data.get('module')
        role_ids = request.data.get('roles', [])

        if module_id:
            module = get_object_or_404(Module, id=module_id)
            roles = Role.objects.filter(id__in=role_ids, module=module)
            user.roles.set(roles)
            action_desc = f"管理員 {request.user.username} 為用戶 {user.username} 分配了模組 {module.name} 和角色 {', '.join([role.name for role in roles])}"
        else:
            user.roles.clear()
            action_desc = f"管理員 {request.user.username} 清除了用戶 {user.username} 的角色"

        user.save()
        record_history(request.user, action_desc)
        return Response({'success': True})
    
    @action(detail=False, methods=['get'])
    def get_role_users(self, request):
        role_id = request.query_params.get('role_id')
        users = User.objects.filter(roles__id=role_id)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        record_history(request.user, f"管理員 {request.user.username} 刪除了用戶 {instance.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        logger.debug(f"收到更新使用者 ID 的請求: {kwargs.get('pk')}")
        return super().update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def get_departments(self, request):
        try:
            departments = User.objects.values(department=F('department_id')).distinct()
            department_list = [dept['department'] for dept in departments if dept['department']]
            return Response(department_list, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving departments: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='get_positions_by_department/(?P<department_id>[^/.]+)')
    def get_positions_by_department(self, request, department_id=None):
        try:
            positions = User.objects.filter(department_id=department_id).values(position=F('position_id')).distinct()
            position_list = [pos['position'] for pos in positions if pos['position']]
            return Response(position_list, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving positions for department {department_id}: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # 記錄更新個人資料的操作
            record_history(user, f"用戶 {user.username} 更新了個人資料")

            return Response({'message': 'Profile updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
# 待審核

class PendingUserViewSet(viewsets.ViewSet):
    queryset = User.objects.filter(is_active=False, is_approved=False)
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve_user(self, request, pk=None):
        try:
            user = User.objects.get(id=pk, is_approved=False)
            user.is_approved = True
            user.is_active = True  # 啟用用戶
            user.save()

            # 記錄開通用戶的操作
            record_history(request.user, f"管理員 {request.user.username} 開通了用戶 {user.username}")

            return Response({'success': True, 'message': '用戶已成功審核'})
        except User.DoesNotExist:
            return Response({'success': False, 'message': '用戶不存在或已審核'}, status=404)

    
class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.filter(is_deleted = False)
    serializer_class = ModuleSerializer

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

        # 記錄刪除模組的操作
        record_history(self.request.user, f"管理員 {self.request.user.username} 刪除了模組 {instance.name}")

        logger.info(f"Module {instance.id} is marked as deleted")
        
    @action(detail=False, methods=['get'])
    def get_modules(self, request):
        modules = Module.objects.filter(is_deleted = False)
        serializer = self.get_serializer(modules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def delete_module(self, request, pk=None):
        module = get_object_or_404(Module, pk=pk)
        module.is_deleted = True
        module.save()

        # 記錄刪除模組的操作
        record_history(request.user, f"管理員 {request.user.username} 刪除了模組 {module.name}")

        return Response(status=status.HTTP_204_NO_CONTENT)
    

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.filter(is_deleted=False)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        module_id = data.get('module')
        users_ids = data.get('users', [])

        if not module_id:
            return Response({'error': 'Module is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        module = get_object_or_404(Module, id=module_id)
        role = Role.objects.create(
            name=data['name'],
            module=module,
            is_active=data.get('is_active', True),
        )
        
        if users_ids:
            users = User.objects.filter(id__in=users_ids)
            role.users.set(users)

        record_history(request.user, f"管理員 {request.user.username} 創建了角色 {role.name} 並分配給用戶 {', '.join([user.username for user in users])}")
        
        serializer = self.get_serializer(role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        # 更新角色基本信息
        module_id = data.get('module')
        users_ids = data.get('users', [])
        if module_id:
            module = get_object_or_404(Module, id=module_id)
            instance.module = module
        if users_ids:
            users = User.objects.filter(id__in=users_ids)
            instance.users.set(users)

        instance.name = data.get('name', instance.name)
        instance.is_active = data.get('is_active', instance.is_active)

        # 更新权限
        permissions = data.get('permissions', [])
        for perm_data in permissions:
            permission = get_object_or_404(RolePermission, id=perm_data['id'])
            permission.can_add = perm_data.get('can_add', permission.can_add)
            permission.can_delete = perm_data.get('can_delete', permission.can_delete)
            permission.can_edit = perm_data.get('can_edit', permission.can_edit)
            permission.can_export = perm_data.get('can_export', permission.can_export)
            permission.can_maintain = perm_data.get('can_maintain', permission.can_maintain)
            permission.can_print = perm_data.get('can_print', permission.can_print)
            permission.can_query = perm_data.get('can_query', permission.can_query)
            permission.can_view = perm_data.get('can_view', permission.can_view)
            permission.save()

        instance.save()

        # 記錄更新角色的操作
        record_history(request.user, f"管理員 {request.user.username} 更新了角色 {instance.name}")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='get_roles_by_module/(?P<pk>\d+)')
    def get_roles_by_module(self, request, pk=None):
        if pk:
            roles = Role.objects.filter(module_id=pk)
            serializer = self.get_serializer(roles, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        role = self.get_object()
        role.is_active = not role.is_active
        role.save()

        # 記錄切換角色狀態的操作
        record_history(request.user, f"管理員 {request.user.username} 切換了角色 {role.name} 的狀態為 {'啟用' if role.is_active else '停用'}")

        return Response({'success': True})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        return Response(data)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('users')
    
    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        role = get_object_or_404(Role, pk=pk)
        role.is_deleted = True
        role.save()

        # 記錄刪除角色的操作
        record_history(request.user, f"管理員 {request.user.username} 刪除了角色 {role.name}")

        return Response(status=status.HTTP_204_NO_CONTENT)


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.filter(is_deleted=False)
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        role_id = self.request.query_params.get('role_id')
        if role_id:
            return self.queryset.filter(role_id=role_id)
        return self.queryset
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        role_id = data.get('role')
        permission_name = data.get('permission_name')

        if not role_id or not permission_name:
            return Response({'error': 'Role and permission name are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        role = get_object_or_404(Role, id=role_id)
        permission = RolePermission.objects.create(
            role=role,
            permission_name=permission_name,
            can_add=data.get('can_add', False),
            can_query=data.get('can_query', False),
            can_view=data.get('can_view', False),
            can_edit=data.get('can_edit', False),
            can_delete=data.get('can_delete', False),
            can_print=data.get('can_print', False),
            can_export=data.get('can_export', False),
            can_maintain=data.get('can_maintain', False)
        )

        # 記錄創建權限的操作
        record_history(request.user, f"管理員 {request.user.username} 為角色 {role.name} 創建了權限 {permission_name}")

        serializer = self.get_serializer(permission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()

        # 記錄刪除權限的操作
        record_history(request.user, f"管理員 {request.user.username} 刪除了角色 {instance.role.name} 的權限 {instance.permission_name}")

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        
        # 更新角色基本信息
        module_id = data.get('module')
        users_ids = data.get('users', [])
        if module_id:
            module = get_object_or_404(Module, id=module_id)
            instance.module = module
        if users_ids:
            users = User.objects.filter(id__in=users_ids)
            instance.users.set(users)
        
        instance.name = data.get('name', instance.name)
        instance.is_active = data.get('is_active', instance.is_active)
        
        # 更新权限
        permissions = data.get('permissions', [])
        for perm_data in permissions:
            permission = get_object_or_404(RolePermission, id=perm_data['id'])
            permission.can_add = perm_data.get('can_add', permission.can_add)
            permission.can_delete = perm_data.get('can_delete', permission.can_delete)
            permission.can_edit = perm_data.get('can_edit', permission.can_edit)
            permission.can_export = perm_data.get('can_export', permission.can_export)
            permission.can_maintain = perm_data.get('can_maintain', permission.can_maintain)
            permission.can_print = perm_data.get('can_print', permission.can_print)
            permission.can_query = perm_data.get('can_query', permission.can_query)
            permission.can_view = perm_data.get('can_view', permission.can_view)
            permission.save()
        
        instance.save()

        # 記錄更新權限的操作
        record_history(request.user, f"管理員 {request.user.username} 更新了角色 {instance.role.name} 的權限 {instance.permission_name}")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class RoleDetailView(APIView):

    def put(self, request, pk, format=None):
        role = get_object_or_404(Role, pk=pk)
        serializer = RoleSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            role = serializer.save()
            role.users.set(request.data.get('users', []))
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            role.users.set(request.data.get('users', []))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 保留 generics 視圖來處理更多CRUD操作：
class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class RoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class RolePermissionListCreateView(generics.ListCreateAPIView):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer

class RolePermissionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer

class ModuleListCreateView(generics.ListCreateAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

class ModuleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

class UserHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = UserHistory.objects.all()
        serializer = UserHistorySerializer(records, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        new_record = UserHistory.objects.create(
            user_id=data['user_id'],
            action=data['action'],
            timestamp=data['timestamp']
        )
        return Response({"message": "Record added successfully", "record_id": new_record.id}, status=status.HTTP_201_CREATED)


class UserPreferencesViewSet(viewsets.ModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer



# 圖表
@api_view(['GET'])
def get_data_sources(request):
    # 返回可用的資料表列表
    data_sources = [
        {"label": "TEST_Inventory", "value": "TEST_Inventory"},
        {"label": "TEST_Products", "value": "TEST_Products"},
        {"label": "TEST_Revenue", "value": "TEST_Revenue"},
        {"label": "TEST_Sales", "value": "TEST_Sales"},
        {"label": "TEST_Stores", "value": "TEST_Stores"}
    ]
    return Response(data_sources)

@api_view(['GET'])
def get_table_fields(request, table_name):
    # 根據 table_name 獲取相應的欄位名稱
    fields = []
    if table_name == "TEST_Inventory":
        fields = [field.name for field in TEST_Inventory._meta.fields]
    elif table_name == "TEST_Products":
        fields = [field.name for field in TEST_Products._meta.fields]
    elif table_name == "TEST_Revenue":
        fields = [field.name for field in TEST_Revenue._meta.fields]
    elif table_name == "TEST_Sales":
        fields = [field.name for field in TEST_Sales._meta.fields]
    elif table_name == "TEST_Stores":
        fields = [field.name for field in TEST_Stores._meta.fields]
    
    return Response(fields)

class ChartDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chart_config = request.data
        chart_type = chart_config.get('chart_type')
        x_data = chart_config.get('x_data')
        y_data = chart_config.get('y_data')

        fig = self.create_chart(chart_type, x_data, y_data)
        chart_json = fig.to_json()
        return JsonResponse(chart_json, safe=False)

    def create_chart(self, chart_type, x_data, y_data):
        if chart_type == 'line':
            return go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='lines')])
        elif chart_type == 'bar':
            return go.Figure(data=[go.Bar(x=x_data, y=y_data)])
        elif chart_type == 'pie':
            return go.Figure(data=[go.Pie(labels=x_data, values=y_data)])
        elif chart_type == 'scatter':
            return go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='markers')])
        # 添加更多圖表類型支持
        return go.Figure()

class ChartConfigurationViewSet(viewsets.ModelViewSet):
    queryset = ChartConfiguration.objects.all()
    serializer_class = ChartConfigurationSerializer
    permission_classes = [IsAuthenticated]

    # def generate_chart(self, configuration):
    #     data = fetch_data_from_source(configuration.data_source, configuration.filter_conditions)
    #     fig = self.create_chart(configuration.chart_type, data[configuration.x_axis_field], data[configuration.y_axis_field])
    #     return fig.to_json()

    def create_chart(self, chart_type, x_data, y_data):
        if chart_type == 'line':
            return go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='lines')])
        elif chart_type == 'bar':
            return go.Figure(data=[go.Bar(x=x_data, y=y_data)])
        elif chart_type == 'pie':
            return go.Figure(data=[go.Pie(labels=x_data, values=y_data)])
        return go.Figure()

    @action(detail=False, methods=['post'])
    def create_chart_action(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            record_history(request.user, f"用户 {request.user.username} 创建了图表 {serializer.data['name']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def update_chart_action(self, request, pk=None):
        chart_config = get_object_or_404(ChartConfiguration, pk=pk)
        serializer = self.get_serializer(chart_config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            record_history(request.user, f"用户 {request.user.username} 更新了图表 {serializer.data['name']}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def revenue_chart_data(request):
    # 獲取營收圖表數據
    revenue_data = TEST_Revenue.objects.values('store_name', 'total_revenue')
    x = [item['store_name'] for item in revenue_data]
    y = [item['total_revenue'] for item in revenue_data]

    # 準備 Plotly 數據
    data = [Bar(x=x, y=y)]
    layout = {'title': '各店營收'}
    chart_json = {
        'data': [d.to_plotly_json() for d in data],
        'layout': layout
    }

    return JsonResponse(chart_json)

@api_view(['GET'])
def sales_chart_data(request):
    # 從資料庫中獲取銷售數據
    sales_data = TEST_Sales.objects.all()
    
    # 創建一個數據框架
    x = [item.store_id for item in sales_data]
    y = [float(item.sale_price) * item.quantity for item in sales_data]  # 假設每個項目有 store_id 和 sale_price

    # 使用 Plotly 創建柱狀圖
    fig = go.Figure(data=[go.Bar(x=x, y=y)])
    fig.update_layout(title='各商店銷售額')

    # 將圖表數據轉換為 JSON 格式
    chart_json = fig.to_plotly_json()
    
    return JsonResponse(chart_json, safe=False)

@api_view(['GET'])
def inventory_chart_data(request):
    # 獲取庫存圖表數據
    inventory_data = TEST_Inventory.objects.values('product_id', 'stock_quantity')
    x = [item['product_id'] for item in inventory_data]
    y = [item['stock_quantity'] for item in inventory_data]

    # 準備 Plotly 數據
    data = [Bar(x=x, y=y)]
    layout = {'title': '各產品庫存量'}
    chart_json = {
        'data': [d.to_plotly_json() for d in data],
        'layout': layout
    }

    return JsonResponse(chart_json)

class InventoryDataAPIView(APIView):
    def get(self, request):
        # 獲取 TEST_Inventory 數據
        inventory_data = list(TEST_Inventory.objects.values())
        return JsonResponse(inventory_data, safe=False)
    
class SalesDataAPIView(APIView):
    def get(self, request):
        # 獲取 TEST_Sales 數據
        sales_data = TEST_Sales.objects.all()
        serializer = SalesDataSerializer(sales_data, many=True)
        return Response(serializer.data)
    
class RevenueDataAPIView(APIView):
    def get(self, request):
        # 獲取 TEST_Revenue 數據
        revenue_data = list(TEST_Revenue.objects.values())
        return JsonResponse(revenue_data, safe=False)
    
