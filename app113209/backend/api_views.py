# app113209\backend\api_views.py
import os
import csv
import uuid
import json
import logging
import xlsxwriter
import plotly.graph_objects as go
from io import BytesIO
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
from django.utils import timezone
from django.db.models import F, Sum  # 添加这行
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from app113209.models import (User, Module, Role,RoleUser, RolePermission, UserHistory, 
                             UserPreferences, ChartConfiguration, TEST_Inventory, 
                             TEST_Revenue, TEST_Sales, TEST_Products, TEST_Stores)
from app113209.serializers import (UserSerializer, ModuleSerializer, RoleSerializer, 
                                   RolePermissionSerializer, UserHistorySerializer,
                                   ChartConfigurationSerializer, SalesDataSerializer,
                                   RevenueDataSerializer, InventoryDataSerializer, UserPreferencesSerializer)
from app113209.utils import record_history
from plotly.graph_objs import Bar, Scatter, Pie
# from generate_chart import save_chart_as_image


logger = logging.getLogger(__name__)

def login_view(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        # 用戶成功登入，更新last_login
        user.last_login = timezone.now()
        user.save()

        login(request, user)
        return JsonResponse({'message': 'Login successful'})
    return JsonResponse({'error': 'Invalid credentials'}, status=400)

def logout_view(request):
    logout(request)
    return JsonResponse({'message': '成功登出'}, status=200)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False, is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # 透過 RoleUser 查詢用戶的角色及其相關的權限
        permissions = RolePermission.objects.filter(
            role__roleuser__user=instance,
            is_deleted=False
        ).values('permission_name', 'can_add', 'can_edit', 'can_delete', 'can_query', 'can_view')

        data['permissions'] = list(permissions)
        return Response(data)

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
       # 檢查當前用戶是否有用戶管理的 can_edit 權限
        permissions = get_user_permissions(request.user.id)
        user_management_permission = permissions.filter(permission_name='用戶管理').first()

        if not any(perm.can_delete for perm in permissions):
            return Response({'error': '您沒有權限刪除此用戶'}, status=status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        record_history(request.user, f"管理員 {request.user.username} 刪除了用戶 {instance.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        #檢查當前用戶是否有用戶管理的 can_edit 權限
        permissions = get_user_permissions(request.user.id)
        user_management_permission = permissions.filter(permission_name='用戶管理').first()

        if not user_management_permission or not user_management_permission.can_edit:
            return Response({'error': '您沒有權限編輯用戶'}, status=status.HTTP_403_FORBIDDEN)
        
        # 允許編輯，執行原有邏輯
        logger.debug(f"收到更新使用者 ID 的請求: {kwargs.get('pk')}")
        response = super().update(request, *args, **kwargs)

        # 紀錄操作
        if response.status_code == status.HTTP_200_OK:
            record_history(request.user, f"管理員{request.user.username} 更新了用戶 {self.get_object().username} 的資料")
        
        return response

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

class UserPermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()  # 添加這行
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        # 透過 RoleUser 查詢用戶的角色及其相關的權限
        permissions = RolePermission.objects.filter(
            role__roleuser__user=user,
            is_deleted=False
        ).values('permission_name', 'can_add', 'can_query', 'can_view', 'can_edit', 'can_delete')

        return Response(list(permissions))


# 待審核

class PendingUserViewSet(viewsets.ViewSet):
    queryset = User.objects.filter(is_active=False, is_approved=False)
    serializer_class = UserSerializer

    def list(self, request):
        # 這裡是列出待審核用戶的邏輯
        users = User.objects.filter(is_active=False, is_approved=False)
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve_user(self, request, pk=None):
        # 檢查當前用戶是否有用戶管理的 can_add 權限
        permissions = get_user_permissions(request.user.id)
        user_management_permission = permissions.filter(permission_name='用戶管理').first()

        if not user_management_permission or not user_management_permission.can_add:
            return Response({'error': '您沒有權限開通用戶'}, status=status.HTTP_403_FORBIDDEN)
        
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
        # 檢查當前用戶是否有角色管理的 can_add 權限
        permissions = get_user_permissions(request.user.id)
        role_management_permission = permissions.filter(permission_name='角色管理').first()

        if not role_management_permission or not role_management_permission.can_add:
            return Response({'error': '您沒有權限新增角色'}, status=status.HTTP_403_FORBIDDEN)

        # 執行原有邏輯進行角色創建
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

        # 記錄操作歷史
        record_history(request.user, f"管理員 {request.user.username} 創建了角色 {role.name} 並分配給用戶 {', '.join([user.username for user in users])}")

        # 返回創建後的角色信息
        serializer = self.get_serializer(role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 檢查當前用戶是否有角色管理的 can_edit 權限
        permissions = get_user_permissions(request.user.id)
        role_management_permission = permissions.filter(permission_name='角色管理').first()

        if not role_management_permission or not role_management_permission.can_edit:
            return Response({'error': '您沒有權限編輯角色'}, status=status.HTTP_403_FORBIDDEN)
        
        # 允許編輯角色，執行原有邏輯
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
        permissions_data = data.get('permissions', [])
        for perm_data in permissions_data:
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
    
    def delete(self, request, *args, **kwargs):
        # 檢查當前用戶是否有角色管理的 can_delete 權限
        permissions = get_user_permissions(request.user.id)
        role_management_permission = permissions.filter(permission_name='角色管理').first()

        if not role_management_permission or not role_management_permission.can_delete:
            return Response({'error': '您沒有權限刪除角色'}, status=status.HTTP_403_FORBIDDEN)

        # 允許刪除角色，執行原有邏輯
        role = self.get_object()
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

def get_user_permissions(user_id):
    # 根據 user_id 查詢角色
    role_user = RoleUser.objects.filter(user_id=user_id).first()
    if not role_user:
        return None
    
    # 查詢該角色的所有權限
    permissions = RolePermission.objects.filter(role_id=role_user.role_id)
    return permissions


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


# 查詢當前登入用戶的偏好
@api_view(['GET'])
def get_user_preferences(request):
    if request.user.is_authenticated:  # 確保用戶已登入
        preferences = UserPreferences.objects.filter(user=request.user)
        serializer = UserPreferencesSerializer(preferences, many=True)
        return Response(serializer.data)
    else:
        return Response({"error": "用戶未登入"}, status=status.HTTP_401_UNAUTHORIZED)

# 更新用戶偏好
@api_view(['PUT'])
def update_user_preference(request, id):
    preference = get_object_or_404(UserPreferences, id=id)
    serializer = UserPreferencesSerializer(preference, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 圖表
# 返回可用的資料表列表
@api_view(['GET'])
def get_data_sources(request):
    data_sources = [
        {"label": "TEST_Inventory", "value": "TEST_Inventory"},
        {"label": "TEST_Products", "value": "TEST_Products"},
        {"label": "TEST_Revenue", "value": "TEST_Revenue"},
        {"label": "TEST_Sales", "value": "TEST_Sales"},
        {"label": "TEST_Stores", "value": "TEST_Stores"}
    ]
    return Response(data_sources)


# 根據資料表獲取欄位
@api_view(['GET'])
def get_table_fields(request, table_name):
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

# 動態生成圖表
def create_chart(chart_type, x_data, y_data):
    if chart_type == 'line':
        fig = go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='lines')])
    elif chart_type == 'bar':
        fig = go.Figure(data=[go.Bar(x=x_data, y=y_data)])
    elif chart_type == 'pie':
        fig = go.Figure(data=[go.Pie(labels=x_data, values=y_data)])
    elif chart_type == 'scatter':
        fig = go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='markers')])
    else:
        fig = go.Figure()  # 返回空白圖表，避免崩潰

    return fig


# API：生成互動圖表（返回JSON格式）
class ChartDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chart_config = request.data
        chart_type = chart_config.get('chart_type')
        x_data = chart_config.get('x_data')
        y_data = chart_config.get('y_data')

        # 確保 x_data 和 y_data 不為空
        if not x_data or not y_data:
            return JsonResponse({'error': 'x_data 和 y_data 不能為空'}, status=400)

        fig = create_chart(chart_type, x_data, y_data)

        # 確保生成圖表正確並轉換為 JSON
        chart_json = fig.to_json()

        # 記錄生成圖表的操作
        record_history(request.user, f"用戶 {request.user.username} 生成了一個 {chart_type} 圖表")
        
        # 返回分析後的數據
        return JsonResponse(chart_json, safe=False)
    
# API：生成圖表並保存為圖片

@api_view(['POST'])
def generate_chart_image(request):
    chart_type = request.data.get('chart_type')
    x_data = request.data.get('x_data')
    y_data = request.data.get('y_data')

    file_name = f"chart_{uuid.uuid4().hex}.png"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    fig = create_chart(chart_type, x_data, y_data)
    fig.write_image(file_path)

    return JsonResponse({'image_path': f"{settings.MEDIA_URL}{file_name}"})

# API：儲存圖表配置
@api_view(['POST'])
def save_chart_configuration(request):
    user = request.user
    config_data = request.data

    ChartConfiguration.objects.create(
        user=user,
        chart_type=config_data['chart_type'],
        data_source=config_data['data_source'],
        x_axis_field=config_data['x_axis_field'],
        y_axis_field=config_data['y_axis_field'],
        filter_conditions=config_data['filter_conditions']
    )
    return Response({"message": "圖表配置已儲存"}, status=201)

# API：根據圖表配置獲取數據
# @api_view(['GET'])
# def get_chart_data(request, chart_id):
#     try:
#         config = get_object_or_404(ChartConfiguration, id=chart_id)
#         data = fetch_data_from_source(config.data_source, config.filter_conditions)
#         return JsonResponse({'x': data[config.x_axis_field], 'y': data[config.y_axis_field]})
#     except Exception as e:
#         logger.error(f"Error fetching chart data: {e}")
#         return JsonResponse({'error': 'Failed to fetch chart data'}, status=500)

# API：儲存與更新圖表配置
class ChartConfigurationViewSet(viewsets.ModelViewSet):
    queryset = ChartConfiguration.objects.all()
    serializer_class = ChartConfigurationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_chart_action(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Chart creation failed: {serializer.errors}")  # 記錄錯誤
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def update_chart_action(self, request, pk=None):
        chart_config = get_object_or_404(ChartConfiguration, pk=pk)
        serializer = self.get_serializer(chart_config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.error(f"Chart update failed: {serializer.errors}")  # 記錄錯誤        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 銷售數據 API
class SalesDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 從資料庫中取得銷售數據
        sales_data = TEST_Sales.objects.all()
        serializer = SalesDataSerializer(sales_data, many=True)
        return Response(serializer.data)

# 營業額數據 API
class RevenueDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 從資料庫中取得營業額數據
        revenue_data = TEST_Revenue.objects.all()
        serializer = RevenueDataSerializer(revenue_data, many=True)
        return Response(serializer.data)

# 庫存數據 API
class InventoryDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 從資料庫中取得庫存數據
        inventory_data = TEST_Inventory.objects.all()
        serializer = InventoryDataSerializer(inventory_data, many=True)
        return Response(serializer.data)

# 銷售量趨勢圖 API
class SalesVolumeChartDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get (self, request):
        # 從資料庫中獲取數據，進行分析
        sales_data = TEST_Sales.objects.values('sale_date').annotate(total_quantity=Sum('quantity'))
        # 這裡根據實際的需求進行篩選和處理
        # 假設需要返回的數據為日期和銷售量
        data = list(sales_data)
        return JsonResponse(data, safe=False)
    
class ProductSalesPieChartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 使用 product__category 來取得相關聯的 product 資訊
        product_sales = TEST_Sales.objects.values('product__category').annotate(total_sales=Sum('quantity'))

        # 準備圓餅圖所需的數據
        data = {
            'categories': [item['product__category'] for item in product_sales],
            'sales': [item['total_sales'] for item in product_sales]
        }

        return JsonResponse(data, safe=False)

# 新增這個函數來生成店鋪的分布數據
# def get_store_distribution():
#     store_data = TEST_Stores.objects.all()

#     # 定義北部、中部、南部、東部的縣市
#     north_regions = ['台北市', '新北市', '基隆市', '新竹市', '桃園市', '新竹縣', '宜蘭縣']
#     center_regions = ['台中市', '苗栗縣', '彰化縣', '南投縣', '雲林縣']
#     south_regions = ['高雄市', '台南市', '嘉義市', '嘉義縣', '屏東縣', '澎湖縣']
#     east_regions = ['花蓮縣', '台東縣']

#     # 計算每個區域內的店鋪數量
#     north = store_data.filter(location__in=north_regions).count()
#     center = store_data.filter(location__in=center_regions).count()
#     south = store_data.filter(location__in=south_regions).count()
#     east = store_data.filter(location__in=east_regions).count()

#     x_data = ['北部', '中部', '南部', '東部']
#     y_data = [north, center, south, east]

#     return x_data, y_data

# 店鋪收益對比圖 API
class StoreComparisonChartDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 從資料庫中獲取各個店鋪的收益數據
        revenue_data = TEST_Revenue.objects.values('store__store_name').annotate(total_revenue=Sum('total_revenue'))
        data = list(revenue_data)
        return JsonResponse(data, safe=False)
    
# @api_view(['POST'])
# def generate_chart_image(request):
#     # 從請求中獲取數據
#     chart_type = request.data.get('chart_type')
#     x_data = request.data.get('x_data')
#     y_data = request.data.get('y_data')

#     # 動態生成文件名
#     file_name = f"chart_{uuid.uuid4().hex}.png"
#     file_path = os.path.join(settings.MEDIA_ROOT, file_name)

#     # 呼叫生成圖表函數
#     save_chart_as_image(chart_type, x_data, y_data, file_path)

#     # 返回生成的圖片路徑
#     return JsonResponse({'image_path': f"{settings.MEDIA_URL}{file_name}"})

# 匯出 CSV
@api_view(['POST'])
def export_data_csv(request):
    data = request.data.get('chartConfig', {}).get('data', [])
    chart_name = request.data.get('chartConfig', {}).get('name', 'chart')  # 獲取圖表名稱
    x_axis_label = request.data.get('chartConfig', {}).get('xAxisLabel', 'X')
    y_axis_label = request.data.get('chartConfig', {}).get('yAxisLabel', 'Y')
    if not data:
        return JsonResponse({"error": "No data provided"}, status=400)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{chart_name}-export.csv"'

    writer = csv.writer(response)
    writer.writerow([x_axis_label, y_axis_label])  # 使用具體的標籤名稱

    for row in data:
        writer.writerow([row['x'], row['y']])

    return response


# 匯出 Excel
@api_view(['POST'])
def export_data_excel(request):
    data = request.data.get('chartConfig', {}).get('data', [])
    chart_name = request.data.get('chartConfig', {}).get('name', 'chart')  # 獲取圖表名稱
    x_axis_label = request.data.get('chartConfig', {}).get('xAxisLabel', 'X')
    y_axis_label = request.data.get('chartConfig', {}).get('yAxisLabel', 'Y')
    if not data:
        return JsonResponse({"error": "No data provided"}, status=400)

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    worksheet.write('A1', x_axis_label)  # 使用具體的標籤名稱
    worksheet.write('B1', y_axis_label)

    for index, row in enumerate(data, start=1):
        worksheet.write(index, 0, row['x'])
        worksheet.write(index, 1, row['y'])

    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{chart_name}-export.xlsx"'

    return response


# 匯出 PDF
@api_view(['POST'])
def export_data_pdf(request):
    data = request.data.get('chartConfig', {}).get('data', [])
    chart_name = request.data.get('chartConfig', {}).get('name', 'chart')  # 獲取圖表名稱
    x_axis_label = request.data.get('chartConfig', {}).get('xAxisLabel', 'X')
    y_axis_label = request.data.get('chartConfig', {}).get('yAxisLabel', 'Y')
    if not data:
        return JsonResponse({"error": "No data provided"}, status=400)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # 設置字體路徑，將其指向你的字體文件目錄
    font_path = os.path.join(settings.BASE_DIR, 'static/fonts/NotoSansTC-Regular.ttf')
    pdfmetrics.registerFont(TTFont('NotoSansTC', font_path))

    # 使用具體的標籤名稱
    p.drawString(100, 750, f"{x_axis_label} | {y_axis_label}")
    y_position = 730

    for row in data:
        p.drawString(100, y_position, f"{row['x']} | {row['y']}")
        y_position -= 20

        if y_position < 100:
            p.showPage()
            p.setFont("NotoSansCJK", 12)
            y_position = 750

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{chart_name}-export.pdf"'

    return response

    return HttpResponse(buffer.read(), content_type='application/pdf')
# 另一個資料庫的測試資料

from  app113209.models import SalesData, StockData  # 確保已經定義這些模型

def dashboard_data(request):
    # 獲取營業額數據
    sales_data = SalesData.objects.all().order_by('sale_date')
    sales_overview = [
        {"date": sale.sale_date, "sales": sale.total_sales} for sale in sales_data
    ]

    # 獲取庫存數據
    stock_data = StockData.objects.all()
    stock_summary = [
        {"product_name": stock.product_name, "stock_quantity": stock.stock_quantity} for stock in stock_data
    ]

    # 返回 JSON 數據
    data = {
        "today_money": sum(sale.total_sales for sale in sales_data),  # 簡單計算總銷售額
        "today_users": 2300,  # 假設這是靜態數據
        "new_clients": 3462,  # 假設這是靜態數據
        "sales": sum(sale.total_sales for sale in sales_data),  # 計算銷售總額
        "sales_overview": sales_overview,
        "stock_summary": stock_summary
    }
    return JsonResponse(data)
from django.http import JsonResponse
from django.db import connection

# 營業額 API
def get_revenue_data(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                DATE(copbf003) AS sale_date,
                resab.resab002 AS branch_name,
                SUM(copbf028) AS total_sales
            FROM 消費帳單資料主檔 AS copbf
            LEFT JOIN 分店設定檔 AS resab 
                ON copbf.copbf980 COLLATE utf8mb4_general_ci = resab.resab001 COLLATE utf8mb4_general_ci
            GROUP BY sale_date, branch_name
            ORDER BY sale_date ASC
        """)
        rows = cursor.fetchall()
    data = [{"sale_date": row[0], "branch_name": row[1], "total_sales": row[2]} for row in rows]
    return JsonResponse(data, safe=False)

# 銷售額 API
def get_sales_data(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                bomaa.bomaa004 AS product_name,
                bomab.bomab003 AS category_name,
                SUM(copbg016) AS total_sales
            FROM 消費帳單明細檔 AS copbg
            LEFT JOIN 料品基本資料主檔 AS bomaa ON copbg.copbg004 = bomaa.bomaa002
            LEFT JOIN 商品分類設定檔 AS bomab ON bomaa.bomaa003 = bomab.bomab002
            GROUP BY product_name, category_name
            ORDER BY total_sales DESC
        """)
        rows = cursor.fetchall()
    data = [{"product_name": row[0], "category_name": row[1], "total_sales": row[2]} for row in rows]
    return JsonResponse(data, safe=False)

# 庫存量 API
def get_stock_data(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                bomaa.bomaa004 AS product_name,
                bomab.bomab003 AS category_name,
                bomaa.bomaa013 AS stock_quantity
            FROM 料品基本資料主檔 AS bomaa
            LEFT JOIN 商品分類設定檔 AS bomab ON bomaa.bomaa003 = bomab.bomab002
            ORDER BY stock_quantity DESC
        """)
        rows = cursor.fetchall()
    data = [{"product_name": row[0], "category_name": row[1], "stock_quantity": row[2]} for row in rows]
    return JsonResponse(data, safe=False)

