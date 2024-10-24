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
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
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

# 自訂權限類別，僅允許具有「系統管理員」角色的使用者存取
class IsSystemAdministrator(BasePermission):
    """
    僅允許具有「系統管理員」角色的使用者存取。
    """

    def has_permission(self, request, view):
        # 取得使用者的角色
        user_roles = Role.objects.filter(
            roleuser__user=request.user,
            is_deleted=False,
            is_active=True
        )
        # 檢查使用者是否有「系統管理員」角色
        return user_roles.filter(name='系統管理員').exists()

# 自訂的 Token 序列化器，用於處理使用者登入時的額外需求
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        logger.debug(f"Received attrs: {attrs}")
        email = attrs.get('email')
        password = attrs.get('password')
        user_type = attrs.get('user_type', 'frontend')  # 默認為 frontend

        # 認證使用者
        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if not user:
            logger.error(f"Authentication failed for email: {email}")
            raise serializers.ValidationError('無效的電子郵件或密碼')

        data = super().validate(attrs)

        remember_me = attrs.get('remember_me', False)

        refresh = self.get_token(self.user)

        # 根據是否選擇「記住我」調整 Token 的有效期
        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=30))
        else:
            refresh.set_exp(lifetime=timedelta(hours=1))

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # 記錄用戶登入歷史，詳細記錄登入類型和時間
        try:
            action_description = f"{'前台' if user_type == 'frontend' else '後台'}登入成功，時間：{timezone.now()}"
            record_history(user, action_description)
            logger.debug(f"Recorded history for user {user.username}: {action_description}")
        except Exception as e:
            logger.error(f"Error recording history for user {user.username}: {e}")

        # 更新 last_login 時間
        try:
            user.last_login = timezone.now()
            user.save()
            logger.debug(f"Updated last_login for user {user.username} to {user.last_login}")
        except Exception as e:
            logger.error(f"Error updating last_login for user {user.username}: {e}")

        return data

# 自訂的 Token 獲取視圖
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# 註冊字體，用於生成 PDF 時使用中文字體
font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'NotoSansTC-Regular.ttf')
if os.path.exists(font_path):
    try:
        pdfmetrics.registerFont(TTFont('NotoSansTC', font_path))
        logger.info("成功註冊字體 'NotoSansTC'")
    except Exception as e:
        logger.error(f"註冊字體 'NotoSansTC' 時出錯: {e}")
else:
    logger.error(f"字體檔案不存在於路徑: {font_path}")

# 使用者登入視圖
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        # 記錄使用者登入歷史，包含時間
        record_history(user, f"用戶 {user.username} 於 {timezone.now()} 登入")
        logger.info(f"User {username} logged in at {timezone.now()}")
        return JsonResponse({'message': 'Login successful'})
    logger.warning(f"Failed login attempt for username: {username}")
    return JsonResponse({'error': 'Invalid credentials'}, status=400)

# 使用者登出視圖
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        # 記錄使用者登出歷史，包含時間
        record_history(request.user, f"用戶 {request.user.username} 於 {timezone.now()} 登出成功")
        logout(request)
        return Response({'message': '成功登出'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"登出時出錯: {e}")
        return Response({'error': '登出失敗'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 使用者 ViewSet，處理使用者的 CRUD 操作
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False, is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # 取得使用者的權限
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
        # 記錄角色分配操作，詳細記錄操作內容
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
        # 記錄刪除用戶操作，包含用戶名和操作者
        record_history(request.user, f"管理員 {request.user.username} 刪除了用戶 {instance.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        # 檢查當前用戶是否有用戶管理的 can_edit 權限
        permissions = get_user_permissions(request.user.id)
        user_management_permission = permissions.filter(permission_name='用戶管理').first()

        if not user_management_permission or not user_management_permission.can_edit:
            return Response({'error': '您沒有權限編輯用戶'}, status=status.HTTP_403_FORBIDDEN)

        # 允許編輯，執行原有邏輯
        logger.debug(f"收到更新使用者 ID 的請求: {kwargs.get('pk')}")
        response = super().update(request, *args, **kwargs)

        # 紀錄操作
        if response.status_code == status.HTTP_200_OK:
            record_history(request.user, f"管理員 {request.user.username} 更新了用戶 {self.get_object().username} 的資料")

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

# 用戶個人資料視圖
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

            # 記錄更新個人資料的操作，包含詳細修改時間
            record_history(user, f"用戶 {user.username} 於 {timezone.now()} 更新了個人資料")

            return Response({'message': '個人資料已成功更新'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 用戶偏好設定 ViewSet
class UserPreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 僅返回當前用戶的偏好設定
        return UserPreferences.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 確保偏好設定關聯到當前用戶
        serializer.save(user=self.request.user)
        # 記錄偏好設定的創建操作
        record_history(self.request.user, f"用戶 {self.request.user.username} 創建了偏好設定")

    def perform_update(self, serializer):
        # 確保更新的是當前用戶的偏好設定
        serializer.save(user=self.request.user)
        # 記錄偏好設定的更新操作
        record_history(self.request.user, f"用戶 {self.request.user.username} 更新了偏好設定")


class UserPermissionViewSet(viewsets.ModelViewSet):
    """
    用戶權限視圖集，提供了用戶權限的相關操作。
    """
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]  # 需要登入認證

    def list(self, request):
        """
        列出當前用戶的所有權限。

        - 透過 `RoleUser` 關聯查詢用戶所屬角色的權限。
        - 回傳權限名稱和各項操作權限的列表。
        """
        user = request.user
        logger.debug(f"Fetching permissions for user: {user.username} (ID: {user.id})")

        # 查詢用戶的角色及其相關的權限
        permissions = RolePermission.objects.filter(
            role__roleuser__user=user,
            is_deleted=False
        ).values(
            'permission_name', 'can_add', 'can_query', 'can_view',
            'can_edit', 'can_delete', 'can_export'
        )

        logger.debug(f"Permissions fetched: {permissions}")
        return Response(list(permissions))

# 待審核用戶視圖集
class PendingUserViewSet(viewsets.ViewSet):
    """
    處理待審核用戶的相關操作。
    """
    queryset = User.objects.filter(is_active=False, is_approved=False)
    serializer_class = UserSerializer

    def list(self, request):
        """
        列出所有待審核的用戶。

        - 查詢未啟用且未審核的用戶。
        - 使用序列化器進行序列化並回傳。
        """
        users = User.objects.filter(is_active=False, is_approved=False)
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve_user(self, request, pk=None):
        """
        審核並啟用用戶。

        - 檢查當前用戶是否有用戶管理的 `can_add` 權限。
        - 若無權限，回傳 403 Forbidden。
        - 將指定的用戶設為已審核並啟用。
        - 若用戶沒有偏好設定，為其創建預設偏好設定。
        - 記錄審核操作的詳細歷史。
        """
        # 檢查當前用戶是否有權限開通用戶
        permissions = get_user_permissions(request.user.id)
        user_management_permission = permissions.filter(permission_name='用戶管理').first()

        if not user_management_permission or not user_management_permission.can_add:
            return Response({'error': '您沒有權限開通用戶'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=pk, is_approved=False)
            user.is_approved = True
            user.is_active = True  # 啟用用戶
            user.save()

            # 檢查是否已經有偏好設定，沒有則創建預設設定
            if not UserPreferences.objects.filter(user=user).exists():
                UserPreferences.objects.create(
                    user=user,
                    fontsize='medium',
                    notificationSettings=1,
                    authentication=1
                )

            # 記錄開通用戶的操作，包含時間和用戶詳情
            record_history(
                request.user,
                f"管理員 {request.user.username} 於 {timezone.now()} 審核並啟用了用戶 {user.username}（ID: {user.id}）"
            )

            return Response({'success': True, 'message': '用戶已成功審核'})
        except User.DoesNotExist:
            # 記錄嘗試審核不存在用戶的操作
            record_history(
                request.user,
                f"管理員 {request.user.username} 於 {timezone.now()} 嘗試審核不存在或已審核的用戶（ID: {pk}）"
            )
            return Response({'success': False, 'message': '用戶不存在或已審核'}, status=404)

class ModuleViewSet(viewsets.ModelViewSet):
    """
    模組視圖集，處理模組的 CRUD 操作。
    """
    queryset = Module.objects.filter(is_deleted=False)
    serializer_class = ModuleSerializer

    def perform_destroy(self, instance):
        """
        刪除模組（軟刪除）。

        - 將模組標記為已刪除。
        - 記錄刪除操作的詳細歷史。
        """
        instance.is_deleted = True
        instance.save()

        # 記錄刪除模組的操作
        record_history(
            self.request.user,
            f"管理員 {self.request.user.username} 於 {timezone.now()} 刪除了模組 {instance.name}（ID: {instance.id}）"
        )

        logger.info(f"Module {instance.id} is marked as deleted")
        
    @action(detail=False, methods=['get'])
    def get_modules(self, request):
        """
        獲取所有未刪除的模組。
        """
        modules = Module.objects.filter(is_deleted=False)
        serializer = self.get_serializer(modules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def delete_module(self, request, pk=None):
        """
        刪除指定的模組。

        - 將模組標記為已刪除。
        - 記錄刪除操作的詳細歷史。
        """
        module = get_object_or_404(Module, pk=pk)
        module.is_deleted = True
        module.save()

        # 記錄刪除模組的操作
        record_history(
            request.user,
            f"管理員 {request.user.username} 於 {timezone.now()} 刪除了模組 {module.name}（ID: {module.id}）"
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

class RoleViewSet(viewsets.ModelViewSet):
    """
    角色視圖集，處理角色的相關操作。
    """
    queryset = Role.objects.filter(is_deleted=False)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        創建新的角色。

        - 檢查當前用戶是否有角色管理的 `can_add` 權限。
        - 若無權限，回傳 403 Forbidden。
        - 創建角色並關聯到指定的模組和用戶。
        - 為新角色自動指派現有圖表的預設權限。
        - 記錄創建操作的詳細歷史。
        """
        # 檢查權限
        permissions = get_user_permissions(request.user.id)
        role_management_permission = permissions.filter(permission_name='角色管理').first()

        if not role_management_permission or not role_management_permission.can_add:
            return Response({'error': '您沒有權限新增角色'}, status=status.HTTP_403_FORBIDDEN)

        # 執行原有邏輯進行角色創建
        data = request.data.copy()
        module_id = data.get('module')
        users_ids = data.get('users', [])

        if not module_id:
            return Response({'error': '必須指定模組'}, status=status.HTTP_400_BAD_REQUEST)
        
        module = get_object_or_404(Module, id=module_id)
        role = Role.objects.create(
            name=data['name'],
            module=module,
            is_active=data.get('is_active', True),
        )
        
        if users_ids:
            users = User.objects.filter(id__in=users_ids)
            role.users.set(users)

        # 為新角色自動指派現有圖表的權限
        chart_configs = ChartConfiguration.objects.filter(is_deleted=False)
        for chart in chart_configs:
            permission_name = slugify(chart.name, allow_unicode=True)
            RolePermission.objects.get_or_create(
                role=role,
                permission_name=permission_name,
                defaults={'can_view': True}
            )

        # 記錄創建角色的操作
        assigned_users = ', '.join([user.username for user in users]) if users_ids else '無'
        record_history(
            request.user,
            f"管理員 {request.user.username} 於 {timezone.now()} 創建了角色 {role.name}（ID: {role.id}），分配給用戶：{assigned_users}"
        )

        # 回傳創建後的角色訊息
        serializer = self.get_serializer(role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        更新角色資訊。

        - 檢查當前用戶是否有角色管理的 `can_edit` 權限。
        - 若無權限，回傳 403 Forbidden。
        - 更新角色的基本信息和權限。
        - 確保系統管理員角色至少有一個用戶。
        - 記錄更新操作的詳細歷史。
        """
        # 檢查權限
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

        # 更新權限
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
        assigned_users = ', '.join([user.username for user in users]) if users_ids else '無'
        record_history(
            request.user,
            f"管理員 {request.user.username} 於 {timezone.now()} 更新了角色 {instance.name}（ID: {instance.id}），分配給用戶：{assigned_users}"
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='get_roles_by_module/(?P<pk>\d+)')
    def get_roles_by_module(self, request, pk=None):
        """
        獲取指定模組下的所有角色。
        """
        if pk:
            roles = Role.objects.filter(module_id=pk, is_deleted=False, is_active=True)
            serializer = self.get_serializer(roles, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        切換角色的啟用狀態。

        - 將角色的 `is_active` 狀態取反。
        - 記錄切換操作的詳細歷史。
        """
        role = self.get_object()
        role.is_active = not role.is_active
        role.save()

        # 記錄切換角色狀態的操作
        record_history(
            request.user,
            f"管理員 {request.user.username} 於 {timezone.now()} 切換了角色 {role.name}（ID: {role.id}）的狀態為 {'啟用' if role.is_active else '停用'}"
        )

        return Response({'success': True})

    def retrieve(self, request, *args, **kwargs):
        """
        獲取指定角色的詳細資訊。
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        return Response(data)
    
    def get_queryset(self):
        """
        重寫 `get_queryset` 方法，預取關聯的用戶資料。
        """
        queryset = super().get_queryset()
        return queryset.prefetch_related('users')
    
    def delete(self, request, *args, **kwargs):
        """
        刪除角色。

        - 檢查當前用戶是否有角色管理的 `can_delete` 權限。
        - 若無權限，回傳 403 Forbidden。
        - 確保系統管理員角色至少有一個用戶。
        - 將角色標記為已刪除。
        - 記錄刪除操作的詳細歷史。
        """
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

        # 記錄刪除角色的操作
        record_history(
            request.user,
            f"管理員 {request.user.username} 於 {timezone.now()} 刪除了角色 {role.name}（ID: {role.id}）"
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

class RolePermissionViewSet(viewsets.ModelViewSet):
    """
    角色權限視圖集，處理角色權限的相關操作。
    """
    queryset = RolePermission.objects.filter(is_deleted=False)
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        根據 `role_id` 過濾權限列表。
        """
        role_id = self.request.query_params.get('role_id')
        if role_id:
            return self.queryset.filter(role_id=role_id)
        return self.queryset
    
    def create(self, request, *args, **kwargs):
        """
        創建新的角色權限。

        - 檢查是否提供了必要的參數。
        - 創建新的權限實例。
        - 記錄創建操作的詳細歷史。
        """
        data = request.data.copy()
        role_id = data.get('role')
        permission_name = data.get('permission_name')

        if not role_id or not permission_name:
            return Response({'error': '必須提供角色和權限名稱'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        record_history(
            request.user,
            f"管理員 {request.user.username} 於 {timezone.now()} 為角色 {role.name}（ID: {role.id}）創建了權限 {permission_name}"
        )

        serializer = self.get_serializer(permission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """
        刪除角色權限。

        - 將權限標記為已刪除。
        - 記錄刪除操作的詳細歷史。
        """
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()

        # 記錄刪除權限的操作
        record_history(
            request.user,
            f"管理員 {request.user.username} 於 {timezone.now()} 刪除了角色 {instance.role.name}（ID: {instance.role.id}）的權限 {instance.permission_name}"
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        """
        更新角色權限。

        - 更新權限的各項操作標誌。
        - 記錄更新操作的詳細歷史。
        """
        instance = self.get_object()
        data = request.data.copy()
        
        # 更新權限信息
        instance.can_add = data.get('can_add', instance.can_add)
        instance.can_delete = data.get('can_delete', instance.can_delete)
        instance.can_edit = data.get('can_edit', instance.can_edit)
        instance.can_export = data.get('can_export', instance.can_export)
        instance.can_maintain = data.get('can_maintain', instance.can_maintain)
        instance.can_print = data.get('can_print', instance.can_print)
        instance.can_query = data.get('can_query', instance.can_query)
        instance.can_view = data.get('can_view', instance.can_view)
        instance.save()

        # 記錄更新權限的操作
        record_history(
            request.user,
            f"管理員 {request.user.username} 於 {timezone.now()} 更新了角色 {instance.role.name}（ID: {instance.role.id}）的權限 {instance.permission_name}"
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# 角色詳細視圖
class RoleDetailView(APIView):
    """
    處理角色的詳細操作，如更新和創建。
    """
    permission_classes = [IsAuthenticated, IsSystemAdministrator]

    def put(self, request, pk, format=None):
        """
        更新指定角色的資訊。
        """
        role = get_object_or_404(Role, pk=pk, is_deleted=False)
        serializer = RoleSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            role = serializer.save()
            role.users.set(request.data.get('users', []))

            # 記錄更新角色的操作
            record_history(
                request.user,
                f"管理員 {request.user.username} 於 {timezone.now()} 更新了角色 {role.name}（ID: {role.id}）"
            )
            logger.info(f"角色 {role.name}（ID: {role.id}）已被更新")

            return Response(serializer.data)
        logger.warning(f"更新角色失敗: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        """
        創建新的角色。
        """
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            role.users.set(request.data.get('users', []))

            # 記錄創建角色的操作
            record_history(
                request.user,
                f"管理員 {request.user.username} 於 {timezone.now()} 創建了角色 {role.name}（ID: {role.id}）"
            )
            logger.info(f"角色 {role.name}（ID: {role.id}）已被創建")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"創建角色失敗: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 保留 generics 視圖來處理更多 CRUD 操作
class RoleListCreateView(generics.ListCreateAPIView):
    """
    列出所有角色並允許創建新角色。
    """
    queryset = Role.objects.filter(is_deleted=False)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsSystemAdministrator]

class RoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    獲取、更新或刪除指定角色。
    """
    queryset = Role.objects.filter(is_deleted=False)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsSystemAdministrator]

class RolePermissionListCreateView(generics.ListCreateAPIView):
    """
    列出所有角色權限並允許創建新權限。
    """
    queryset = RolePermission.objects.filter(is_deleted=False)
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated, IsSystemAdministrator]

class RolePermissionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    獲取、更新或刪除指定角色權限。
    """
    queryset = RolePermission.objects.filter(is_deleted=False)
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated, IsSystemAdministrator]

# 獲取使用者的所有權限
def get_user_permissions(user_id):
    """
    獲取指定使用者的所有權限。

    Args:
        user_id (int): 使用者的 ID。

    Returns:
        QuerySet: 使用者擁有的所有角色權限。
    """
    role_users = RoleUser.objects.filter(user_id=user_id, role__is_deleted=False, role__is_active=True)
    if not role_users.exists():
        return RolePermission.objects.none()

    permissions = RolePermission.objects.filter(
        role__in=role_users.values_list('role_id', flat=True),
        is_deleted=False
    ).distinct()
    return permissions

# 模組列表與創建視圖
class ModuleListCreateView(generics.ListCreateAPIView):
    """
    列出所有模組並允許創建新模組。
    """
    queryset = Module.objects.filter(is_deleted=False)
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsSystemAdministrator]

# 模組詳細視圖
class ModuleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    獲取、更新或刪除指定模組。
    """
    queryset = Module.objects.filter(is_deleted=False)
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsSystemAdministrator]

# 用戶歷史紀錄視圖
class UserHistoryListView(APIView):
    """
    處理用戶歷史紀錄的查看和新增。
    """
    permission_classes = [IsAuthenticated, IsSystemAdministrator]

    def get(self, request):
        """
        獲取所有用戶的歷史紀錄。
        """
        records = UserHistory.objects.all()
        serializer = UserHistorySerializer(records, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        新增一條用戶歷史紀錄。
        """
        data = request.data
        try:
            new_record = UserHistory.objects.create(
                user_id=data['user_id'],
                action=data['action'],
                timestamp=data.get('timestamp', timezone.now())
            )
            record_history(
                request.user,
                f"新增用戶歷史紀錄: 用戶ID {new_record.user_id}，操作: {new_record.action}，時間: {new_record.timestamp}"
            )
            logger.info(f"新增用戶歷史紀錄: {new_record}")
            return Response({"message": "Record added successfully", "record_id": new_record.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"新增用戶歷史紀錄時出錯: {e}")
            return Response({"error": "新增歷史紀錄失敗"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Signal receiver 防止移除最後一個系統管理員
@receiver(m2m_changed, sender=RoleUser)
def prevent_last_admin_removal(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    信號接收器，防止移除最後一個系統管理員角色的用戶。
    """
    if instance.id == 1 and action in ['pre_remove', 'pre_clear']:
        admin_users = instance.users.exclude(pk__in=pk_set)
        if not admin_users.exists():
            logger.warning(f"嘗試移除最後一個系統管理員用戶，操作被阻止")
            raise IntegrityError('至少需要一個系統管理員，無法移除最後一個系統管理員。')

# 返回可用的資料表列表
@api_view(['GET'])
def get_data_sources(request):
    """
    獲取所有可用的資料來源列表，供前端選擇。
    """
    data_sources = [
        {"label": "TEST_Inventory", "value": "TEST_Inventory"},
        {"label": "TEST_Products", "value": "TEST_Products"},
        {"label": "TEST_Revenue", "value": "TEST_Revenue"},
        {"label": "TEST_Sales", "value": "TEST_Sales"},
        {"label": "TEST_Stores", "value": "TEST_Stores"}
    ]
    logger.info("獲取資料來源列表成功")
    return Response(data_sources)

# 模型對應字典，用於動態查詢
MODEL_MAPPING = {
    'TEST_Inventory': TEST_Inventory,
    'TEST_Products': TEST_Products,
    'TEST_Revenue': TEST_Revenue,
    'TEST_Sales': TEST_Sales,
    'TEST_Stores': TEST_Stores,
    'Branch': Branch,
    # 如有其他模型，請繼續添加
}

# 動態圖表數據生成
@api_view(['POST'])
def dynamic_chart_data(request):
    """
    根據請求參數動態生成圖表數據。
    """
    table_name = request.data.get('table_name')
    x_field = request.data.get('x_field')
    y_field = request.data.get('y_field')
    join_fields = request.data.get('join_fields', [])
    filter_conditions = request.data.get('filter_conditions', {})
    ordering = request.data.get('ordering', None)
    limit = request.data.get('limit', None)

    logger.info(f"從表 {table_name} 獲取數據，x_field={x_field}, y_field={y_field}, 過濾條件={filter_conditions}, 排序={ordering}, 限制={limit}")

    if not table_name:
        logger.error("請求缺少 table_name")
        return JsonResponse({'error': 'table_name 未提供'}, status=400)

    model = MODEL_MAPPING.get(table_name)
    if not model:
        logger.error(f"找不到表 {table_name} 對應的模型")
        return JsonResponse({'error': '資料表不存在'}, status=400)

    # 驗證 x_field 和 y_field 是否存在於模型中
    if not validate_lookup(model, x_field):
        logger.error(f"x_field {x_field} 在模型 {table_name} 中不存在")
        return JsonResponse({'error': f"x_field {x_field} 不存在於資料表 {table_name}"}, status=400)
    if not validate_lookup(model, y_field):
        logger.error(f"y_field {y_field} 在模型 {table_name} 中不存在")
        return JsonResponse({'error': f"y_field {y_field} 不存在於資料表 {table_name}"}, status=400)

    try:
        queryset = model.objects.all()

        # 處理關聯字段
        select_related_fields = get_select_related_fields(x_field) + get_select_related_fields(y_field)
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)

        # 處理過濾條件
        if isinstance(filter_conditions, dict) and filter_conditions:
            queryset = queryset.filter(**filter_conditions)

        # 處理排序
        if ordering:
            queryset = queryset.order_by(*ordering)

        # 處理限制（如前10條）
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

        logger.info(f"返回圖表數據，x_data 長度: {len(x_data)}, y_data 長度: {len(y_data)}, 最後更新時間: {last_updated}")
        return JsonResponse({'x_data': x_data, 'y_data': y_data, 'last_updated': last_updated})
    except Exception as e:
        logger.error(f"生成動態圖表數據時出錯: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def get_select_related_fields(field_name):
    """
    獲取需要使用 select_related 的關聯字段。

    Args:
        field_name (str): 欄位名稱，可能包含 '__' 進行多層關聯。

    Returns:
        list: 關聯字段的列表。
    """
    parts = field_name.split('__')
    if len(parts) > 1:
        # 返回所有關聯字段的路徑
        return ['__'.join(parts[:i]) for i in range(1, len(parts))]
    else:
        return []

def get_fields_metadata(model, prefix='', visited_models=None):
    """
    獲取模型的欄位元數據，包括關聯欄位的相關模型和欄位。

    Args:
        model (models.Model): Django 模型類。
        prefix (str, optional): 欄位前綴，用於多層關聯。默認為空字串。
        visited_models (set, optional): 已訪問的模型集，用於防止循環引用。默認為 None。

    Returns:
        list: 欄位元數據的列表。
    """
    if visited_models is None:
        visited_models = set()
    model_name = model.__name__
    if model_name in visited_models:
        return []
    visited_models.add(model_name)

    fields_metadata = []
    for field in model._meta.get_fields():
        if field.auto_created and not field.concrete:
            continue  # 跳過自動生成的反向關聯欄位
        field_name = f"{prefix}{field.name}"
        field_info = {
            'name': field_name,
            'type': field.get_internal_type(),
            'verbose_name': field.verbose_name,
            'choices': field.choices if hasattr(field, 'choices') else None,
            'related_model': field.related_model.__name__ if field.is_relation else None
        }
        fields_metadata.append(field_info)

        # 如果是外鍵，遞歸獲取關聯模型的欄位
        if field.is_relation and field.related_model and not field.many_to_many:
            # 避免循環引用，限制遞歸深度
            if len(prefix.split('__')) < 2:
                related_fields = get_fields_metadata(field.related_model, prefix=f"{field_name}__", visited_models=visited_models)
                fields_metadata.extend(related_fields)
    return fields_metadata

@api_view(['GET'])
def get_table_fields_metadata(request, table_name):
    """
    獲取指定資料表的所有欄位元數據。

    Args:
        request (HttpRequest): 請求對象。
        table_name (str): 資料表名稱。

    Returns:
        Response: 包含欄位元數據的 JSON 回應。
    """
    try:
        model = MODEL_MAPPING.get(table_name)
        if not model:
            logger.error(f"查詢的資料表 {table_name} 不存在")
            return Response({'error': '資料表不存在'}, status=400)

        fields_metadata = get_fields_metadata(model)
        logger.info(f"成功獲取資料表 {table_name} 的欄位元數據")
        return Response({'fields': fields_metadata})
    except Exception as e:
        logger.error(f"獲取資料表 {table_name} 的欄位元數據時出錯: {e}")
        return Response({'error': '無法獲取欄位資訊'}, status=500)

@api_view(['GET'])
def get_options(request, related_model):
    """
    返回指定相關模型的選項，通常用於前端的選擇組件。

    Args:
        request (HttpRequest): 請求對象。
        related_model (str): 相關模型名稱。

    Returns:
        Response: 包含選項的 JSON 回應。
    """
    try:
        model = apps.get_model(app_label='app113209', model_name=related_model)
        if not model:
            logger.error(f"相關模型 {related_model} 不存在")
            return Response({'error': '相關模型不存在'}, status=400)

        # 根據具體需求調整返回的選項
        if related_model == 'TEST_Products':
            options = model.objects.values('product_id', 'product_name')
            options = [{'value': item['product_id'], 'label': item['product_name']} for item in options]
        elif related_model == 'Branch':  # 假設有 Branch 模型
            options = model.objects.values('branch_id', 'branch_name')
            options = [{'value': item['branch_id'], 'label': item['branch_name']} for item in options]
        else:
            options = []

        logger.info(f"成功獲取相關模型 {related_model} 的選項")
        return Response({'options': options})
    except Exception as e:
        logger.error(f"獲取相關模型 {related_model} 的選項時出錯: {e}")
        return Response({'error': '無法獲取選項'}, status=500)

def save_chart_as_image(fig):
    """
    將圖表保存為圖片並返回其路徑。

    Args:
        fig (plotly.graph_objects.Figure): 要保存的圖表對象。

    Returns:
        str: 圖片的 URL 路徑。
    """
    file_name = f"chart_{uuid.uuid4().hex}.png"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    fig.write_image(file_path)
    logger.info(f"圖表已保存為圖片: {file_path}")
    return f"{settings.MEDIA_URL}{file_name}"

# 動態生成圖表
def create_chart(chart_type, x_data, y_data):
    """
    根據指定的圖表類型和數據生成 Plotly 圖表對象。

    Args:
        chart_type (str): 圖表類型，如 'line', 'bar', 'pie'。
        x_data (list): X 軸數據。
        y_data (list): Y 軸數據。

    Returns:
        plotly.graph_objects.Figure: 生成的圖表對象。
    """
    try:
        if chart_type == 'line':
            fig = go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='lines')])
        elif chart_type == 'bar':
            fig = go.Figure(data=[go.Bar(x=x_data, y=y_data)])
        elif chart_type == 'pie':
            fig = go.Figure(data=[go.Pie(labels=x_data, values=y_data)])
        else:
            raise ValueError(f"不支持的圖表類型: {chart_type}")
        
        logger.info(f"成功生成 {chart_type} 圖表")
        return fig
    except Exception as e:
        logger.error(f"生成圖表時出錯: {e}")
        return go.Figure()

# API：生成互動圖表（返回JSON格式）
class ChartDataAPIView(APIView):
    """
    生成互動圖表數據，返回 JSON 格式。
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        根據請求參數生成圖表數據。
        """
        chart_config = request.data
        x_field = chart_config.get('x_field')
        y_field = chart_config.get('y_field')
        filter_conditions = chart_config.get('filter_conditions')

        # 確保 API 收到請求並記錄相關資訊
        logger.debug(f"生成互動圖表，x_field: {x_field}, y_field: {y_field}, filter_conditions: {filter_conditions}")

        # 檢查是否有正確的 x_data 和 y_data
        if not x_field or not y_field:
            logger.error("請求缺少 x_field 或 y_field")
            return JsonResponse({'error': 'x_data 和 y_data 不能為空'}, status=400)

        # 模擬數據處理，實際應根據需求從資料庫或模型中獲取數據
        x_data = get_x_data(x_field)  # 實現 get_x_data 函數以從資料庫中獲取 x_data
        y_data = get_y_data(y_field)  # 實現 get_y_data 函數以從資料庫中獲取 y_data

        logger.info(f"互動圖表數據生成成功，x_data 長度: {len(x_data)}, y_data 長度: {len(y_data)}")
        return JsonResponse({'x_data': x_data, 'y_data': y_data})

# 獲取指定資料表的欄位和相關欄位
@api_view(['GET'])
def get_table_fields(request, table_name):
    """
    獲取指定資料表的所有欄位及其相關模型的欄位。

    Args:
        request (HttpRequest): 請求對象。
        table_name (str): 資料表名稱。

    Returns:
        JsonResponse: 包含欄位和相關欄位的資料。
    """
    try:
        model = MODEL_MAPPING.get(table_name)
        if not model:
            logger.error(f"查詢的資料表 {table_name} 不存在")
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

        logger.info(f"成功獲取資料表 {table_name} 的欄位和相關欄位")
        return JsonResponse({'fields': fields, 'related_fields': related_fields})
    except Exception as e:
        logger.error(f"獲取資料表 {table_name} 的欄位時出錯: {e}")
        return JsonResponse({'error': '無法獲取欄位'}, status=500)

# API：儲存圖表配置
@api_view(['POST'])
def save_chart_configuration(request):
    """
    儲存新的圖表配置。
    """
    user = request.user
    config_data = request.data

    try:
        chart_config = ChartConfiguration.objects.create(
            user=user,
            chart_type=config_data['chart_type'],
            data_source=config_data['data_source'],
            x_axis_field=config_data['x_axis_field'],
            y_axis_field=config_data['y_axis_field'],
            filter_conditions=config_data.get('filter_conditions', '{}')
        )

        # 記錄圖表配置的創建操作
        record_history(
            user,
            f"用戶 {user.username} 於 {timezone.now()} 創建了圖表配置 {chart_config.name}（ID: {chart_config.id}）"
        )
        logger.info(f"用戶 {user.username} 創建了圖表配置 {chart_config.name}（ID: {chart_config.id}）")

        return JsonResponse({'message': '圖表已儲存', 'id': chart_config.id}, status=201)
    except Exception as e:
        logger.error(f"儲存圖表配置時出錯: {e}")
        return JsonResponse({'error': '圖表儲存失敗'}, status=500)

# API：獲取所有圖表配置
@api_view(['GET'])
def get_chart_configuration(request):
    """
    獲取所有未刪除的圖表配置。
    """
    try:
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
        logger.info("成功獲取所有圖表配置")
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"獲取圖表配置時出錯: {e}")
        return JsonResponse({'error': '無法獲取圖表配置'}, status=500)

# API：獲取圖表數據
@api_view(['GET'])
def get_chart_data(request, table_name):
    """
    獲取指定資料表的圖表數據。

    Args:
        request (HttpRequest): 請求對象。
        table_name (str): 資料表名稱。

    Returns:
        JsonResponse: 包含 x_data 和 y_data 的資料。
    """
    x_field = request.GET.get('x_field')
    y_field = request.GET.get('y_field')

    # 使用 MODEL_MAPPING 字典
    model = MODEL_MAPPING.get(table_name)
    if not model:
        logger.error(f"查詢的資料表 {table_name} 不存在")
        return JsonResponse({'error': '資料表不存在'}, status=400)

    try:
        queryset = model.objects.all()

        # 提取 x_field 和 y_field 的數據
        data = list(queryset.values_list(x_field, y_field))

        x_data = [item[0] for item in data]
        y_data = [item[1] for item in data]

        logger.info(f"成功獲取圖表數據，表: {table_name}, x_field: {x_field}, y_field: {y_field}")
        return JsonResponse({'x_data': x_data, 'y_data': y_data})
    except Exception as e:
        logger.error(f"獲取圖表數據時出錯: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# API：儲存與更新圖表配置
class ChartConfigurationViewSet(viewsets.ModelViewSet):
    """
    圖表配置視圖集，處理圖表配置的 CRUD 操作。
    """
    queryset = ChartConfiguration.objects.filter(is_deleted=False)
    serializer_class = ChartConfigurationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='preview_role')
    def preview_role(self, request):
        """
        預覽指定角色可查看的圖表配置。
        """
        role_id = request.query_params.get('role_id')
        if not role_id:
            logger.error("請求缺少 role_id")
            return Response({'error': 'role_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        role = get_object_or_404(Role, id=role_id, is_deleted=False, is_active=True)
        # 獲取該角色可查看的圖表
        permission_names = RolePermission.objects.filter(
            role=role,
            can_view=True,
            is_deleted=False
        ).values_list('permission_name', flat=True)

        # 直接使用 permission_name 匹配圖表的 name
        charts = self.get_queryset().filter(
            name__in=permission_names
        )
        serializer = self.get_serializer(charts, many=True)
        logger.info(f"角色 {role.name}（ID: {role.id}）可查看的圖表配置已被獲取")
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        列出當前使用者有權查看的所有圖表配置，並附加相關的操作權限信息。
        """
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

        logger.info(f"使用者 {request.user.username} 已獲取其可查看的圖表配置列表")
        return Response(visible_charts)

    @action(detail=False, methods=['post'])
    def create_chart_action(self, request):
        """
        創建新的圖表配置並自動為所有活動角色添加查看權限。
        """
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            try:
                chart_config = serializer.save()
            except IntegrityError:
                logger.error(f"創建圖表配置失敗，名稱已存在: {data.get('name')}")
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

            # 記錄創建圖表配置的操作
            record_history(
                request.user,
                f"管理員 {request.user.username} 於 {timezone.now()} 創建了圖表配置 {chart_config.name}（ID: {chart_config.id}）並為所有活動角色添加了查看權限"
            )
            logger.info(f"圖表配置 {chart_config.name}（ID: {chart_config.id}）已創建並為所有活動角色添加了查看權限")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"創建圖表配置失敗: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='update-chart')
    def update_chart(self, request, pk=None):
        """
        更新指定的圖表配置，並在名稱變更時更新相關權限名稱。
        """
        chart_config = get_object_or_404(ChartConfiguration, pk=pk, is_deleted=False)
        serializer = self.get_serializer(chart_config, data=request.data, partial=True)
        if serializer.is_valid():
            old_name = chart_config.name
            chart_config = serializer.save()
            new_name = chart_config.name

            if old_name != new_name:
                # 更新相關權限名稱
                update_permission_name(old_name, new_name)

                # 記錄操作歷史
                record_history(
                    request.user,
                    f"管理員 {request.user.username} 於 {timezone.now()} 更新了圖表名稱從 '{old_name}' 到 '{new_name}'，並更新了相關權限名稱"
                )
                logger.info(f"圖表名稱從 '{old_name}' 更新到 '{new_name}' 並更新相關權限名稱")

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

            logger.info(f"圖表配置 {new_name}（ID: {chart_config.id}）的權限信息已更新")
            return Response(data)
        logger.error(f"更新圖表配置失敗: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def delete_chart(self, request, pk=None):
        """
        軟刪除指定的圖表配置，並標記相關權限為已刪除。
        """
        try:
            chart_config = get_object_or_404(ChartConfiguration, pk=pk, is_deleted=False)
            chart_config.is_deleted = True  # 標記為已刪除
            chart_config.save()

            # 使用 utils.py 中的函數來更新權限名稱
            permission_name = slugify(chart_config.name, allow_unicode=True)
            RolePermission.objects.filter(permission_name=permission_name).update(is_deleted=True)

            # 記錄刪除圖表配置的操作
            record_history(
                request.user,
                f"管理員 {request.user.username} 於 {timezone.now()} 刪除了圖表配置 {chart_config.name}（ID: {chart_config.id}）並標記相關權限為已刪除"
            )
            logger.info(f"圖表配置 {chart_config.name}（ID: {chart_config.id}）已被軟刪除，相關權限標記為已刪除")

            return Response({"message": "圖表已被刪除"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"刪除圖表配置時出錯: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """
        獲取指定圖表配置的詳細資訊。
        """
        try:
            chart_config = self.get_object()
            serializer = self.get_serializer(chart_config)
            logger.info(f"成功獲取圖表配置 {chart_config.name}（ID: {chart_config.id}）的詳細資訊")
            return Response(serializer.data)
        except ChartConfiguration.DoesNotExist:
            logger.warning(f"圖表配置 ID {pk} 未找到")
            return Response({'error': 'Chart not found'}, status=status.HTTP_404_NOT_FOUND)

    # 恢復隱藏的圖表配置（目前註解中）
    # @action(detail=True, methods=['post'])
    # def restore_chart(self, request, pk=None):
    #     """
    #     恢復已刪除的圖表配置。
    #     """
    #     chart_config = get_object_or_404(ChartConfiguration, pk=pk, is_deleted=True)
    #     chart_config.is_deleted = False
    #     chart_config.save()

    #     # 記錄恢復操作
    #     record_history(
    #         request.user,
    #         f"用戶 {request.user.username} 於 {timezone.now()} 恢復了圖表配置 {chart_config.chart_type}"
    #     )
    #     logger.info(f"圖表配置 {chart_config.chart_type}（ID: {chart_config.id}）已被恢復")

    #     return Response({"message": "圖表已恢復"}, status=status.HTTP_200_OK)

# 銷售數據 API
class SalesDataAPIView(APIView):
    """
    獲取銷售數據，進行聚合後返回。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        獲取銷售數據，按日期聚合總銷售量。
        """
        try:
            sales_data = TEST_Sales.objects.values('sale_date').annotate(total_sales=Sum('quantity'))
            logger.info("成功獲取銷售數據")
            return JsonResponse(list(sales_data), safe=False)
        except Exception as e:
            logger.error(f"獲取銷售數據時出錯: {e}")
            return JsonResponse({'error': 'Failed to fetch sales data'}, status=500)

# 營業額數據 API
class RevenueDataAPIView(APIView):
    """
    獲取營業額數據，返回序列化後的資料。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        獲取所有營業額數據。
        """
        try:
            revenue_data = TEST_Revenue.objects.all()
            serializer = RevenueDataSerializer(revenue_data, many=True)
            logger.info("成功獲取營業額數據")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"獲取營業額數據時出錯: {e}")
            return JsonResponse({'error': 'Failed to fetch revenue data'}, status=500)

# 庫存數據 API
class InventoryDataAPIView(APIView):
    """
    獲取庫存數據，按分店聚合總庫存量。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        獲取庫存數據，按分店聚合總庫存量。
        """
        try:
            inventory_data = TEST_Inventory.objects.values('branch_id').annotate(total_stock=Sum('stock_quantity'))
            logger.info("成功獲取庫存數據")
            return JsonResponse(list(inventory_data), safe=False)
        except Exception as e:
            logger.error(f"獲取庫存數據時出錯: {e}")
            return JsonResponse({'error': 'Failed to fetch inventory data'}, status=500)

# 銷售量趨勢圖 API
class SalesVolumeChartDataAPIView(APIView):
    """
    獲取銷售量趨勢圖數據，按日期聚合總銷售量。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        獲取銷售量趨勢圖數據。
        """
        try:
            sales_data = TEST_Sales.objects.values('sale_date').annotate(total_quantity=Sum('quantity'))
            data = list(sales_data)
            logger.info("成功獲取銷售量趨勢圖數據")
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"獲取銷售量趨勢圖數據時出錯: {e}")
            return JsonResponse({'error': 'Failed to fetch sales volume data'}, status=500)

# 產品銷售圓餅圖 API
class ProductSalesPieChartAPIView(APIView):
    """
    獲取產品銷售圓餅圖數據，按產品類別聚合總銷售量。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        獲取產品銷售圓餅圖數據。
        """
        try:
            product_sales = TEST_Sales.objects.select_related('product_id').values('product_id__category').annotate(total_sales=Sum('quantity'))
            data = {
                'categories': [item['product_id__category'] for item in product_sales],
                'sales': [item['total_sales'] for item in product_sales]
            }
            logger.info("成功獲取產品銷售圓餅圖數據")
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"獲取產品銷售圓餅圖數據時出錯: {e}")
            return JsonResponse({'error': 'Failed to fetch product sales data'}, status=500)

# 店鋪收益對比圖 API
class StoreComparisonChartDataAPIView(APIView):
    """
    獲取店鋪收益對比圖數據，按店鋪聚合總營業額。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        獲取店鋪收益對比圖數據。
        """
        try:
            # 調整欄位名稱以符合資料表結構
            revenue_data = TEST_Revenue.objects.values('store_id').annotate(total_revenue=Sum('total_revenue'))
            data = list(revenue_data)
            logger.info("成功獲取店鋪收益對比圖數據")
            return JsonResponse(data, safe=False)
        except Exception as e:
            logger.error(f"獲取店鋪收益對比圖數據時出錯: {e}")
            return JsonResponse({'error': 'Failed to fetch revenue data'}, status=500)

# 驗證查詢字段路徑是否存在於模型中
def validate_lookup(model, lookup):
    """
    驗證給定的查詢字段路徑是否在模型中存在。

    Args:
        model (models.Model): Django 模型類。
        lookup (str): 查詢字段路徑，例如 'product__category__name'。

    Returns:
        bool: 如果查詢路徑存在，返回 True，否則返回 False。
    """
    parts = lookup.split('__')
    current_model = model
    for part in parts:
        try:
            field = current_model._meta.get_field(part)
            if field.is_relation:
                current_model = field.related_model
            else:
                # 如果不是關聯字段，且不是最後一個部分，則路徑無效
                if part != parts[-1]:
                    return False
        except FieldDoesNotExist:
            return False
    return True


# 匯出 CSV
@api_view(['POST'])
def export_data(request):
    """
    處理匯出資料的請求，支援 CSV、Excel 和 PDF 格式。

    步驟：
    1. 獲取請求中的圖表配置。
    2. 根據圖表配置確定要匯出的資料表和字段。
    3. 從資料庫中獲取資料。
    4. 根據指定的格式進行匯出。
    5. 回傳匯出的檔案。

    Args:
        request (HttpRequest): Django 的 HTTP 請求對象。

    Returns:
        HttpResponse: 包含匯出檔案的 HTTP 回應。
    """
    logger.info("收到匯出請求")
    
    # 從請求中獲取圖表配置
    chart_config = request.data.get('chartConfig', {})
    table_name = chart_config.get('data_source', '')
    export_all = request.data.get('export_all', False)  # 判斷是否匯出所有字段
    format = request.data.get('format')  # 確定匯出格式
    chart_name = chart_config.get('name', 'chart')  # 圖表名稱，預設為 'chart'

    x_field = chart_config.get('x_axis_field')  # X 軸字段
    y_field = chart_config.get('y_axis_field')  # Y 軸字段

    logger.debug(f"正在匯出圖表: {chart_name}, 資料表: {table_name}, X 字段: {x_field}, Y 字段: {y_field}, 格式: {format}, 是否匯出所有字段: {export_all}")

    # 檢查資料來源是否指定
    if not table_name:
        logger.error("資料來源未指定")
        return JsonResponse({"error": "資料來源未指定"}, status=400)

    # 根據資料表名稱取得對應的模型
    model = MODEL_MAPPING.get(table_name)
    if not model:
        logger.error(f"資料表不存在: {table_name}")
        return JsonResponse({"error": "資料表不存在"}, status=400)

    # 決定要匯出的字段
    if export_all:
        fields = [field.name for field in model._meta.fields]  # 匯出所有字段
    else:
        if not x_field or not y_field:
            logger.error("x_axis_field 和 y_axis_field 是必填的")
            return JsonResponse({"error": "x_axis_field 和 y_axis_field 是必填的"}, status=400)
        fields = [x_field, y_field]  # 只匯出指定的 X 和 Y 字段

    try:
        # 從資料庫中獲取資料
        data = list(model.objects.values(*fields))
        logger.debug(f"已獲取匯出資料: {len(data)} 筆記錄")

        # 根據格式進行匯出
        if format == 'csv':
            response = export_to_csv(data, chart_name, fields)
        elif format == 'excel':
            response = export_to_excel(data, chart_name, fields)
        elif format == 'pdf':
            response = export_to_pdf(data, chart_name, fields)
        else:
            logger.error(f"不支援的匯出格式: {format}")
            return JsonResponse({"error": "不支援的匯出格式"}, status=400)

        logger.info(f"匯出成功: 圖表 {chart_name} 以格式 {format} 匯出")
        
        # 記錄匯出操作到歷史紀錄
        record_history(
            user=request.user,
            action=f"匯出圖表 '{chart_name}' 來源資料表 '{table_name}'，格式為 '{format}'，匯出字段: {fields}",
            timestamp=timezone.now()
        )
        
        return response
    except Exception as e:
        logger.error(f"匯出資料時發生錯誤: {e}")
        return JsonResponse({"error": str(e)}, status=500)

def export_to_csv(data, chart_name, fields):
    """
    將資料匯出為 CSV 格式。

    Args:
        data (list): 要匯出的資料列表。
        chart_name (str): 圖表名稱，作為檔案名稱。
        fields (list): 欄位名稱列表。

    Returns:
        HttpResponse: 包含 CSV 檔案的 HTTP 回應。
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{chart_name}.csv"'
    writer = csv.writer(response)
    
    # 寫入表頭
    writer.writerow(fields)
    
    # 寫入每一行資料
    for row in data:
        writer.writerow([row.get(field, '') for field in fields])
    
    # 記錄匯出為 CSV 的操作
    record_history(
        user=request.user,
        action=f"將圖表 '{chart_name}' 資料匯出為 CSV 格式，共匯出 {len(data)} 筆記錄",
        timestamp=timezone.now()
    )
    
    return response

def export_to_excel(data, chart_name, fields):
    """
    將資料匯出為 Excel 格式。

    Args:
        data (list): 要匯出的資料列表。
        chart_name (str): 圖表名稱，作為檔案名稱。
        fields (list): 欄位名稱列表。

    Returns:
        HttpResponse: 包含 Excel 檔案的 HTTP 回應。
    """
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'remove_timezone': True})
    worksheet = workbook.add_worksheet()
    
    # 寫入表頭
    for col, field in enumerate(fields):
        worksheet.write(0, col, field)
    
    # 寫入每一行資料
    for row_idx, row in enumerate(data, start=1):
        for col_idx, field in enumerate(fields):
            worksheet.write(row_idx, col_idx, row.get(field, ''))
    
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{chart_name}.xlsx"'
    
    # 記錄匯出為 Excel 的操作
    record_history(
        user=request.user,
        action=f"將圖表 '{chart_name}' 資料匯出為 Excel 格式，共匯出 {len(data)} 筆記錄",
        timestamp=timezone.now()
    )
    
    return response

def export_to_pdf(data, chart_name, fields):
    """
    將資料匯出為 PDF 格式。

    Args:
        data (list): 要匯出的資料列表。
        chart_name (str): 圖表名稱，作為檔案名稱。
        fields (list): 欄位名稱列表。

    Returns:
        HttpResponse: 包含 PDF 檔案的 HTTP 回應。
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("NotoSansTC", 12)  # 使用已註冊的字體名稱
    
    # 在 PDF 中寫入圖表名稱
    p.drawString(100, 750, f"{chart_name}")
    
    # 寫入表頭
    header = " | ".join(fields)
    p.drawString(100, 730, header)
    y_position = 710
    
    # 寫入每一行資料
    for row in data:
        row_data = " | ".join([str(row.get(field, '')) for field in fields])
        p.drawString(100, y_position, row_data)
        y_position -= 20
        if y_position < 50:  # 若頁面空間不足，新增頁面
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
    
    # 記錄匯出為 PDF 的操作
    record_history(
        user=request.user,
        action=f"將圖表 '{chart_name}' 資料匯出為 PDF 格式，共匯出 {len(data)} 筆記錄",
        timestamp=timezone.now()
    )
    
    return response

# 另一個資料庫的測試資料

from app113209.models import SalesData, StockData  # 確保已經定義這些模型

def dashboard_data(request):
    """
    獲取儀表板所需的營業額和庫存數據，並返回 JSON 格式的回應。

    步驟：
    1. 獲取營業額數據並進行匯總。
    2. 獲取庫存數據並進行匯總。
    3. 組裝所有數據並回傳。

    Args:
        request (HttpRequest): Django 的 HTTP 請求對象。

    Returns:
        JsonResponse: 包含儀表板數據的 JSON 回應。
    """
    try:
        # 獲取營業額數據，按日期排序
        sales_data = SalesData.objects.all().order_by('sale_date')
        sales_overview = [
            {"date": sale.sale_date, "sales": sale.total_sales} for sale in sales_data
        ]

        # 獲取庫存數據
        stock_data = StockData.objects.all()
        stock_summary = [
            {"product_name": stock.product_name, "stock_quantity": stock.stock_quantity} for stock in stock_data
        ]

        # 組裝返回的 JSON 數據
        data = {
            "today_money": sum(sale.total_sales for sale in sales_data),  # 簡單計算總銷售額
            "today_users": 2300,  # 假設這是靜態數據
            "new_clients": 3462,  # 假設這是靜態數據
            "sales": sum(sale.total_sales for sale in sales_data),  # 計算銷售總額
            "sales_overview": sales_overview,
            "stock_summary": stock_summary
        }
        logger.info(f"成功獲取儀表板數據，總銷售額: {data['sales']}")
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"獲取儀表板數據時發生錯誤: {e}")
        return JsonResponse({"error": "無法獲取儀表板數據"}, status=500)

from django.db import connection

# 營業額 API
# @csrf_exempt
def get_revenue_data(request):
    """
    獲取營業額數據，按分店和日期匯總。

    Args:
        request (HttpRequest): Django 的 HTTP 請求對象。

    Returns:
        JsonResponse: 包含營業額數據的 JSON 回應。
    """
    try:
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
        
        # 組裝查詢結果為 JSON 格式
        data = [{"sale_date": row[0], "branch_name": row[1], "total_sales": row[2]} for row in rows]
        logger.info(f"成功獲取營業額數據，共 {len(data)} 筆記錄")
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"獲取營業額數據時發生錯誤: {e}")
        return JsonResponse({"error": "無法獲取營業額數據"}, status=500)

# 銷售額 API
def get_sales_data(request):
    """
    獲取銷售額數據，按產品和類別匯總。

    Args:
        request (HttpRequest): Django 的 HTTP 請求對象。

    Returns:
        JsonResponse: 包含銷售額數據的 JSON 回應。
    """
    try:
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
        
        # 組裝查詢結果為 JSON 格式
        data = [{"product_name": row[0], "category_name": row[1], "total_sales": row[2]} for row in rows]
        logger.info(f"成功獲取銷售額數據，共 {len(data)} 筆記錄")
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"獲取銷售額數據時發生錯誤: {e}")
        return JsonResponse({"error": "無法獲取銷售額數據"}, status=500)

# 庫存量 API
def get_stock_data(request):
    """
    獲取庫存量數據，按產品和類別匯總。

    Args:
        request (HttpRequest): Django 的 HTTP 請求對象。

    Returns:
        JsonResponse: 包含庫存量數據的 JSON 回應。
    """
    try:
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
        
        # 組裝查詢結果為 JSON 格式
        data = [{"product_name": row[0], "category_name": row[1], "stock_quantity": row[2]} for row in rows]
        logger.info(f"成功獲取庫存量數據，共 {len(data)} 筆記錄")
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"獲取庫存量數據時發生錯誤: {e}")
        return JsonResponse({"error": "無法獲取庫存量數據"}, status=500)
