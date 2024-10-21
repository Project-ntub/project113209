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
from datetime import timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.apps import apps
from django.db import models
from django.db import IntegrityError
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import F, Sum
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import FieldDoesNotExist
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, status, generics, serializers
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from app113209.models import (User, Module, Role, RoleUser, RolePermission, UserHistory, 
                             UserPreferences, ChartConfiguration, TEST_Inventory, 
                             TEST_Revenue, TEST_Sales, TEST_Products, TEST_Stores, Branch)
from app113209.serializers import (UserSerializer, ModuleSerializer, RoleSerializer, 
                                   RolePermissionSerializer, UserHistorySerializer,
                                   ChartConfigurationSerializer, SalesDataSerializer,
                                   RevenueDataSerializer, InventoryDataSerializer, UserPreferencesSerializer)
from app113209.utils import record_history, update_permission_name

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        logger.debug(f"Received attrs: {attrs}")
        email = attrs.get('email')
        password = attrs.get('password')
        user_type = attrs.get('user_type', 'frontend')  # 默認為 frontend

        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if not user:
            logger.error(f"Authentication failed for email: {email}")
            raise serializers.ValidationError('無效的電子郵件或密碼')

        data = super().validate(attrs)

        remember_me = attrs.get('remember_me', False)

        refresh = self.get_token(self.user)

        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=30))
        else: 
            refresh.set_exp(lifetime=timedelta(hours=1))

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # 記錄用戶登入歷史
        try:
            action_description = '前台登入成功' if user_type == 'frontend' else '後台登入成功'
            record_history(user, action_description)
            logger.debug(f"Recorded history for user {user.username}: {action_description}")
        except Exception as e:
            logger.error(f"Error recording history for user {user.username}: {e}")

        # 更新 last_login
        try:
            user.last_login = timezone.now()
            user.save()
            logger.debug(f"Updated last_login for user {user.username} to {user.last_login}")
        except Exception as e:
            logger.error(f"Error updating last_login for user {user.username}: {e}")

        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# 註冊字體
font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'NotoSansTC-Regular.ttf')
if os.path.exists(font_path):
    try:
        pdfmetrics.registerFont(TTFont('NotoSansTC', font_path))
        logger.info("成功註冊字體 'NotoSansTC'")
    except Exception as e:
        logger.error(f"註冊字體 'NotoSansTC' 時出錯: {e}")
else:
    logger.error(f"字體檔案不存在於路徑: {font_path}")

def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        record_history(user, '用戶登入')
        logger.info(f"User {username} logged in at {timezone.now()}")
        return JsonResponse({'message': 'Login successful'})
    logger.warning(f"Failed login attempt for username: {username}")
    return JsonResponse({'error': 'Invalid credentials'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        record_history(request.user, '登出成功')
        return Response({'message': '成功登出'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"登出時出錯: {e}")
        return Response({'error': '登出失敗'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    
    def destroy(self, request, *args, **kwargs):
        permissions = get_user_permissions(request.user.id)
        user_management_permission = permissions.filter(permission_name='用戶管理').first()

        if not any(perm.can_delete for perm in permissions):
            return Response({'error': '您沒有權限刪除此用戶'}, status=status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()

        # 檢查用戶是否是系統管理員
        is_system_admin = RolePermission.objects.filter(
            permission_name=slugify("用戶管理", allow_unicode=True),
            can_view=True,
            is_deleted=False
        ).exists()

        if is_system_admin:
            # 檢查是否是最後一個系統管理員
            admin_users = User.objects.filter(roles__id=1, is_deleted=False)
            if admin_users.count() <= 1:
                return Response({'error': '至少需要一個系統管理員，無法刪除此用戶'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 標記用戶為已刪除
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

class UserPreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 僅返回當前用戶的偏好設定
        return UserPreferences.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 確保偏好設定關聯到當前用戶
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # 確保更新的是當前用戶的偏好設定
        serializer.save(user=self.request.user)

class UserPermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        logger.debug(f"Fetching permissions for user: {user.username} (ID: {user.id})")

        # 透過 RoleUser 查詢用戶的角色及其相關的權限
        permissions = RolePermission.objects.filter(
            role__roleuser__user=user,
            is_deleted=False
        ).values('permission_name', 'can_add', 'can_query', 'can_view', 'can_edit', 'can_delete', 'can_export')

        logger.debug(f"Permissions fetched: {permissions}")
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

            # 檢查是否已經有偏好設定，沒有澤創建預設設定
            if not UserPreferences.objects.filter(user=user).exists():
                UserPreferences.objects.create(user=user, fontsize='medium', notificationSettings=1, authentication=1)

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

        # 檢查系統管理員角色是否仍有用戶
        if instance.id == 1:
            admin_users = User.objects.filter(roles__id=1, is_deleted=False)
            if admin_users.count() < 1:
                return Response({'error': '系統管理員角色至少需要一個用戶'}, status=status.HTTP_400_BAD_REQUEST)

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
        permissions = get_user_permissions(request.user.id)
        role_management_permission = permissions.filter(permission_name='角色管理').first()

        if not role_management_permission or not role_management_permission.can_delete:
            return Response({'error': '您沒有權限刪除角色'}, status=status.HTTP_403_FORBIDDEN)
        
        role = self.get_object()

        # 如果刪除的是系統管理員角色，檢查是否有其他用戶
        if role.id == 1:
            admin_users = User.objects.filter(roles__id=1, is_deleted=False)
            if admin_users.count() <= 1:
                return Response({'error': '至少需要一個系統管理員，無法刪除此角色'}, status=status.HTTP_400_BAD_REQUEST)

        role.is_deleted = True
        role.save()
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
    role_users = RoleUser.objects.filter(user_id=user_id)
    if not role_users.exists():
        return RolePermission.objects.none()
    
    permissions = RolePermission.objects.filter(
        role__in=role_users.values_list('role_id', flat=True),
        is_deleted=False
    ).distinct()
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


# # 查詢當前登入用戶的偏好
# @api_view(['GET'])
# def get_user_preferences(request):
#     if request.user.is_authenticated:  # 確保用戶已登入
#         preferences = UserPreferences.objects.filter(user=request.user)
#         serializer = UserPreferencesSerializer(preferences, many=True)
#         return Response(serializer.data)
#     else:
#         return Response({"error": "用戶未登入"}, status=status.HTTP_401_UNAUTHORIZED)

# # 更新用戶偏好
# @api_view(['PUT'])
# def update_user_preference(request, id):
#     preference = get_object_or_404(UserPreferences, id=id)
#     serializer = UserPreferencesSerializer(preference, data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@receiver(m2m_changed, sender=RoleUser)
def prevent_last_admin_removal(sender, instance, action, reverse, model, pk_set, **kwargs):
    if instance.id == 1 and action in ['pre_remove', 'pre_clear']:
        admin_users = instance.users.exclude(pk__in=pk_set)
        if not admin_users.exists():
            raise IntegrityError('至少需要一個系統管理員，無法移除最後一個系統管理員。')

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


MODEL_MAPPING = {
    'TEST_Inventory': TEST_Inventory,
    'TEST_Products': TEST_Products,
    'TEST_Revenue': TEST_Revenue,
    'TEST_Sales': TEST_Sales,
    'TEST_Stores': TEST_Stores,
    'Branch': Branch,
    # 如有其他模型，請繼續添加
}

@api_view(['POST'])
def dynamic_chart_data(request):
    table_name = request.data.get('table_name')
    x_field = request.data.get('x_field')
    y_field = request.data.get('y_field')
    join_fields = request.data.get('join_fields', [])
    filter_conditions = request.data.get('filter_conditions', {})
    ordering = request.data.get('ordering', None)
    limit = request.data.get('limit', None)

    logger.info(f"Fetching data from {table_name} with x_field={x_field}, y_field={y_field}, filters={filter_conditions}, ordering={ordering}, limit={limit}")

    if not table_name:
        logger.error("table_name 未提供")
        return JsonResponse({'error': 'table_name 未提供'}, status=400)

    model = MODEL_MAPPING.get(table_name)
    if not model:
        logger.error(f"Model for table {table_name} not found in MODEL_MAPPING")
        return JsonResponse({'error': '資料表不存在'}, status=400)

    # 驗證 x_field 和 y_field
    if not validate_lookup(model, x_field):
        logger.error(f"x_field {x_field} does not exist in model {table_name}")
        return JsonResponse({'error': f"x_field {x_field} 不存在於資料表 {table_name}"}, status=400)
    if not validate_lookup(model, y_field):
        logger.error(f"y_field {y_field} does not exist in model {table_name}")
        return JsonResponse({'error': f"y_field {y_field} 不存在於資料表 {table_name}"}, status=400)

    try:
        queryset = model.objects.all()

        # 處理關聯字段
        if join_fields:
            logger.info(f"Using join_fields with fields: {join_fields}")
            queryset = queryset.select_related(*join_fields)

        # 處理過濾條件
        if isinstance(filter_conditions, dict) and filter_conditions:
            for key, value in filter_conditions.items():
                if isinstance(value, dict):
                    for op, val in value.items():
                        filter_key = f"{key}__{op}"
                        queryset = queryset.filter(**{filter_key: val})
                else:
                    queryset = queryset.filter(**{key: value})

        # 處理排序
        if ordering:
            queryset = queryset.order_by(*ordering)

        # 處理限制（如前10）
        if isinstance(limit, int):
            queryset = queryset[:limit]

        # 聚合數據：按 x_field 分組並聚合 y_field
        aggregated_data = queryset.values(x_field).annotate(y_sum=Sum(y_field))
        x_data = [item[x_field] for item in aggregated_data]
        y_data = [float(item['y_sum']) if item['y_sum'] is not None else 0 for item in aggregated_data]

        # 獲取最後更新時間
        last_updated_field = 'last_update' if hasattr(model, 'last_update') else (
            'last_updated' if hasattr(model, 'last_updated') else (
                'created_at' if hasattr(model, 'created_at') else None
            )
        )

        if last_updated_field:
            last_updated_instance = queryset.order_by(f'-{last_updated_field}').first()
            last_updated = getattr(last_updated_instance, last_updated_field) if last_updated_instance else None
        else:
            last_updated = None

        logger.info(f"Returning x_data length: {len(x_data)}, y_data length: {len(y_data)}")
        return JsonResponse({'x_data': x_data, 'y_data': y_data, 'last_updated': last_updated})
    except Exception as e:
        logger.error(f"Error in dynamic_chart_data: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_table_fields_metadata(request, table_name):
    """
    返回指定資料表的欄位元數據，包括欄位名稱、類型及選項（如果有）。
    """
    try:
        model = MODEL_MAPPING.get(table_name)
        if not model:
            return Response({'error': '資料表不存在'}, status=400)
        
        fields_metadata = []
        for field in model._meta.get_fields():
            if field.auto_created and not field.concrete:
                continue  # 跳過自動生成的反向關聯字段
            field_info = {
                'name': field.name,
                'type': field.get_internal_type(),
                'verbose_name': field.verbose_name,
                'choices': field.choices if hasattr(field, 'choices') else None,
                'related_model': field.related_model.__name__ if field.is_relation else None
            }
            fields_metadata.append(field_info)
        
        return Response({'fields': fields_metadata})
    except Exception as e:
        logger.error(f"Error fetching table metadata for {table_name}: {e}")
        return Response({'error': '無法獲取欄位資訊'}, status=500)
    
@api_view(['GET'])
def get_options(request, related_model):
    """
    返回指定相關模型的選項，通常用於 SelectFilter 或 CheckboxFilter 組件。
    """
    try:
        model = apps.get_model(app_label='app113209', model_name=related_model)
        if not model:
            return Response({'error': '相關模型不存在'}, status=400)
        
        # 假設我們要返回該模型的所有實例的某個字段作為選項
        # 根據具體需求調整
        # 例如，假設我們要返回 TEST_Products 的 product_id 和 product_name
        if related_model == 'TEST_Products':
            options = model.objects.values('product_id', 'product_name')
            options = [{'value': item['product_id'], 'label': item['product_name']} for item in options]
        elif related_model == 'Branch':  # 假設有 Branch 模型
            options = model.objects.values('branch_id', 'branch_name')
            options = [{'value': item['branch_id'], 'label': item['branch_name']} for item in options]
        else:
            options = []

        return Response({'options': options})
    except Exception as e:
        logger.error(f"Error fetching options for model {related_model}: {e}")
        return Response({'error': '無法獲取選項'}, status=500)

def save_chart_as_image(fig):
    file_name = f"chart_{uuid.uuid4().hex}.png"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    fig.write_image(file_path)
    return f"{settings.MEDIA_URL}{file_name}"    
   
# 動態生成圖表
def create_chart(chart_type, x_data, y_data):
    try:
        if chart_type == 'line':
            fig = go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='lines')])
        elif chart_type == 'bar':
            fig = go.Figure(data=[go.Bar(x=x_data, y=y_data)])
        elif chart_type == 'pie':
            fig = go.Figure(data=[go.Pie(labels=x_data, values=y_data)])
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        return fig
    except Exception as e:
        logger.error(f"An error occurred while creating the chart: {e}")
        return go.Figure()



# API：生成互動圖表（返回JSON格式）
class ChartDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chart_config = request.data
        x_field = chart_config.get('x_field')
        y_field = chart_config.get('y_field')
        filter_conditions = chart_config.get('filter_conditions')

        # 這裡加上log來確保API收到請求
        print(f"X Field: {x_field}, Y Field: {y_field}, Filters: {filter_conditions}")

        # 檢查是否有正確的 x_data 和 y_data
        if not x_field or not y_field:
            return JsonResponse({'error': 'x_data 和 y_data 不能為空'}, status=400)

        # 模擬數據處理
        x_data = get_x_data(x_field)  # 從資料庫或模型中獲取x_data
        y_data = get_y_data(y_field)  # 從資料庫或模型中獲取y_data

        return JsonResponse({'x_data': x_data, 'y_data': y_data})



@api_view(['GET'])
def get_table_fields(request, table_name):
    try:
        model = MODEL_MAPPING.get(table_name)
        if not model:
            return JsonResponse({'error': '資料表不存在'}, status=400)

        # 取得當前模型的欄位列表
        fields = [field.name for field in model._meta.fields]

        # 取得關聯欄位（ForeignKey）
        related_fields = {}
        for field in model._meta.fields:
            if isinstance(field, models.ForeignKey):
                related_model = field.related_model
                related_field_names = [f.name for f in related_model._meta.fields]
                related_fields[field.name] = {
                    'related_model': related_model.__name__,
                    'fields': related_field_names
                }

        return JsonResponse({'fields': fields, 'related_fields': related_fields})
    except Exception as e:
        logger.error(f"Error retrieving table fields: {e}")
        return JsonResponse({'error': '無法獲取欄位'}, status=500)


    
# API：儲存圖表配置
@api_view(['POST'])
def save_chart_configuration(request):
    user = request.user
    config_data = request.data

    chart_config = ChartConfiguration.objects.create(
        user=user,
        chart_type=config_data['chart_type'],
        data_source=config_data['data_source'],
        x_axis_field=config_data['x_axis_field'],
        y_axis_field=config_data['y_axis_field'],
        filter_conditions=config_data.get('filter_conditions', '{}')
    )
    return JsonResponse({'message': '圖表已儲存', 'id': chart_config.id}, status=201)

@api_view(['GET'])
def get_chart_configuration(request):
    configs = ChartConfiguration.objects.filter(is_deleted=False)
    data = []
    for config in configs:
        data.append({
            "id": config.id,
            "name": config.name,
            "chart_type": config.chart_type.lower(),  # 確保是小寫
            "x_axis_field": config.x_axis_field,
            "y_axis_field": config.y_axis_field,
            "data_source": config.data_source
        })
    return JsonResponse(data, safe=False)

@api_view(['GET'])
def get_chart_data(request, table_name):
    x_field = request.GET.get('x_field')
    y_field = request.GET.get('y_field')

    # 使用 MODEL_MAPPING 字典
    model = MODEL_MAPPING.get(table_name)
    if not model:
        return JsonResponse({'error': '資料表不存在'}, status=400)

    try:
        queryset = model.objects.all()

        # 提取 x_field 和 y_field 的数据
        data = list(queryset.values_list(x_field, y_field))

        x_data = [item[0] for item in data]
        y_data = [item[1] for item in data]

        return JsonResponse({'x_data': x_data, 'y_data': y_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API：儲存與更新圖表配置
class ChartConfigurationViewSet(viewsets.ModelViewSet):
    queryset = ChartConfiguration.objects.filter(is_deleted=False)
    serializer_class = ChartConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # 獲取用戶的所有權限名稱，其中 can_view=True
        permission_names = RolePermission.objects.filter(
            role__roleuser__user=request.user,
            can_view=True,
            is_deleted=False
        ).values_list('permission_name', flat=True)

        # 獲取所有圖表配置
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # 篩選用戶有權查看的圖表（使用 allow_unicode=True 的 slugify）
        visible_charts = [chart for chart in data if slugify(chart['name'], allow_unicode=True) in permission_names]

        # 為每個可見圖表添加其他權限信息
        for chart in visible_charts:
            permission_name = slugify(chart['name'], allow_unicode=True)
            role_permissions = RolePermission.objects.filter(
                permission_name=permission_name,
                role__roleuser__user=request.user,
                is_deleted=False
            )
            chart['can_edit'] = role_permissions.filter(can_edit=True).exists()
            chart['can_delete'] = role_permissions.filter(can_delete=True).exists()
            chart['can_export'] = role_permissions.filter(can_export=True).exists()

        return Response(visible_charts)

    @action(detail=False, methods=['post'])
    def create_chart_action(self, request):
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            try:
                chart_config = serializer.save()
            except IntegrityError:
                return Response({'error': '圖表名稱已存在，請選擇其他名稱'}, status=status.HTTP_400_BAD_REQUEST)

            # 使用 allow_unicode=True 的 slugify
            permission_name = slugify(chart_config.name, allow_unicode=True)

            # 自動為所有活動的角色添加權限，預設 can_view=True
            active_roles = Role.objects.filter(is_active=True, is_deleted=False)
            for role in active_roles:
                RolePermission.objects.get_or_create(
                    role=role,
                    permission_name=permission_name,
                    defaults={'can_view': True}
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Chart creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='update-chart')
    def update_chart(self, request, pk=None):
        chart_config = get_object_or_404(ChartConfiguration, pk=pk)
        serializer = self.get_serializer(chart_config, data=request.data, partial=True)
        if serializer.is_valid():
            old_name = chart_config.name
            chart_config = serializer.save()
            new_name = chart_config.name

            if old_name != new_name:
                # 移除 "chart_" 前綴
                update_permission_name(old_name, new_name)

                # 記錄操作歷史
                record_history(request.user, f"管理員 {request.user.username} 更新了圖表名稱從 '{old_name}' 到 '{new_name}'，並更新了相關權限名稱")

            # 添加權限信息
            data = serializer.data
            permission_name = slugify(new_name, allow_unicode=True)
            data['can_edit'] = RolePermission.objects.filter(
                permission_name=permission_name,
                role__roleuser__user=request.user,
                can_edit=True
            ).exists()
            data['can_delete'] = RolePermission.objects.filter(
                permission_name=permission_name,
                role__roleuser__user=request.user,
                can_delete=True
            ).exists()
            data['can_export'] = RolePermission.objects.filter(
                permission_name=permission_name,
                role__roleuser__user=request.user,
                can_export=True
            ).exists()

            return Response(data)
        logger.error(f"Chart update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def delete_chart(self, request, pk=None):
        try:
            chart_config = get_object_or_404(ChartConfiguration, pk=pk)
            chart_config.is_deleted = True  # 標記為已刪除
            chart_config.save()

            # 使用 utils.py 中的函數來更新權限名稱
            permission_name = slugify(chart_config.name, allow_unicode=True)
            RolePermission.objects.filter(permission_name=permission_name).update(is_deleted=True)

            return Response({"message": "圖表已被刪除"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting chart: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
            try:
                chart_config = self.get_object()
                serializer = self.get_serializer(chart_config)
                return Response(serializer.data)
            except ChartConfiguration.DoesNotExist:
                return Response({'error': 'Chart not found'}, status=status.HTTP_404_NOT_FOUND)

    # 恢復隱藏的圖表
    # @action(detail=True, methods=['post'])
    # def restore_chart(self, request, pk=None):
    #     chart_config = get_object_or_404(ChartConfiguration, pk=pk)
        
    #     chart_config.is_deleted = False
    #     chart_config.save()

    #     # 記錄恢復操作
    #     record_history(request.user, f"用戶 {request.user.username} 恢復了圖表 {chart_config.chart_type}")

    #     return Response({"message": "圖表已恢復"}, status=status.HTTP_200_OK)

# 銷售數據 API
class SalesDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            sales_data = TEST_Sales.objects.values('sale_date').annotate(total_sales=Sum('quantity'))
            return JsonResponse(list(sales_data), safe=False)
        except Exception as e:
            logger.error(f"Error fetching sales chart data: {e}")
            return JsonResponse({'error': 'Failed to fetch sales data'}, status=500)

# 營業額數據 API
class RevenueDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 從資料庫中取得營業額數據
            revenue_data = TEST_Revenue.objects.all()
            serializer = RevenueDataSerializer(revenue_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching revenue data: {e}")
            return JsonResponse({'error': 'Failed to fetch revenue data'}, status=500)

# 庫存數據 API
class InventoryDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            inventory_data = TEST_Inventory.objects.values('branch_id').annotate(total_stock=Sum('stock_quantity'))
            return JsonResponse(list(inventory_data), safe=False)
        except Exception as e:
            logger.error(f"Error fetching inventory chart data: {e}")
            return JsonResponse({'error': 'Failed to fetch inventory data'}, status=500)

# 銷售量趨勢圖 API
class SalesVolumeChartDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            sales_data = TEST_Sales.objects.values('sale_date').annotate(total_quantity=Sum('quantity'))
            data = list(sales_data)
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"Error fetching sales volume chart data: {e}")
            return JsonResponse({'error': 'Failed to fetch sales volume data'}, status=500)

# 產品銷售圓餅圖 API
class ProductSalesPieChartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            product_sales = TEST_Sales.objects.select_related('product_id').values('product_id__category').annotate(total_sales=Sum('quantity'))
            data = {
                'categories': [item['product_id__category'] for item in product_sales],
                'sales': [item['total_sales'] for item in product_sales]
            }
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"Error fetching product sales pie chart data: {e}")
            return JsonResponse({'error': 'Failed to fetch product sales data'}, status=500)


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
# 調整欄位名稱以符合你的資料表結構
        revenue_data = TEST_Revenue.objects.values('store_id').annotate(total_revenue=Sum('total_revenue'))
        data = list(revenue_data)
        return JsonResponse(data, safe=False)
    
def validate_lookup(model, lookup):
    """
    驗證給定的查詢欄位路徑是否在模型中存在。

    Args:
        model (models.Model): Django 模型類。
        lookup (str): 查詢欄位路徑，例如 'product__category'。

    Returns:
        bool: 如果查詢路徑存在，返回 True，否則返回 False。
    """
    parts = lookup.split('__')
    current_model = model
    for part in parts:
        try:
            field = current_model._meta.get_field(part)
            if isinstance(field, models.ForeignKey):
                current_model = field.related_model
        except FieldDoesNotExist:
            return False
    return True

# 匯出 CSV
@api_view(['POST'])
def export_data(request):
    logger.info("Received export request")
    chart_config = request.data.get('chartConfig', {})
    table_name = chart_config.get('data_source', '')
    export_all = request.data.get('export_all', False)  # 新增參數判斷是否匯出所有字段
    format = request.data.get('format')
    chart_name = chart_config.get('name', 'chart')

    x_field = chart_config.get('x_axis_field')
    y_field = chart_config.get('y_axis_field')

    logger.debug(f"Exporting chart: {chart_name}, table: {table_name}, x_field: {x_field}, y_field: {y_field}, format: {format}, export_all: {export_all}")

    if not table_name:
        logger.error("資料來源未指定")
        return JsonResponse({"error": "資料來源未指定"}, status=400)

    model = MODEL_MAPPING.get(table_name)
    if not model:
        logger.error(f"資料表不存在: {table_name}")
        return JsonResponse({"error": "資料表不存在"}, status=400)

    # 決定要匯出的字段
    if export_all:
        fields = [field.name for field in model._meta.fields]
    else:
        if not x_field or not y_field:
            logger.error("x_axis_field 和 y_axis_field 是必填的")
            return JsonResponse({"error": "x_axis_field 和 y_axis_field 是必填的"}, status=400)
        fields = [x_field, y_field]

    try:
        data = list(model.objects.values(*fields))
        logger.debug(f"Fetched data for export: {len(data)} records")

        if format == 'csv':
            response = export_to_csv(data, chart_name, fields)
        elif format == 'excel':
            response = export_to_excel(data, chart_name, fields)
        elif format == 'pdf':
            response = export_to_pdf(data, chart_name, fields)
        else:
            logger.error(f"Unsupported format: {format}")
            return JsonResponse({"error": "Unsupported format"}, status=400)

        logger.info(f"Export successful for chart: {chart_name} in format: {format}")
        return response
    except Exception as e:
        logger.error(f"Error in export_data: {e}")
        return JsonResponse({"error": str(e)}, status=500)

def export_to_csv(data, chart_name, fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{chart_name}.csv"'
    writer = csv.writer(response)
    
    # 寫入表頭
    writer.writerow(fields)
    
    for row in data:
        writer.writerow([row.get(field, '') for field in fields])
    return response

def export_to_excel(data, chart_name, fields):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    
    # 寫入表頭
    for col, field in enumerate(fields):
        worksheet.write(0, col, field)
    
    for row_idx, row in enumerate(data, start=1):
        for col_idx, field in enumerate(fields):
            worksheet.write(row_idx, col_idx, row.get(field, ''))
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{chart_name}.xlsx"'
    return response

def export_to_pdf(data, chart_name, fields):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("NotoSansTC", 12)  # 使用已註冊的字體名稱
    p.drawString(100, 750, f"{chart_name}")

    # 寫入表頭
    header = " | ".join(fields)
    p.drawString(100, 730, header)
    y_position = 710
    for row in data:
        row_data = " | ".join([str(row.get(field, '')) for field in fields])
        p.drawString(100, y_position, row_data)
        y_position -= 20
        if y_position < 50:  # 新增頁面
            p.showPage()
            p.setFont("NotoSansTC", 12)
            p.drawString(100, 750, f"{chart_name} (續)")
            p.drawString(100, 730, header)
            y_position = 710

    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{chart_name}.pdf"'
    return response


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
from django.views.decorators.csrf import csrf_exempt

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

