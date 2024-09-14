# app113209\backend\views.py
import logging
import uuid
import json
from app113209.models import User, Role, RolePermission, Module, UserHistory, Branch
from app113209.serializers import UserSerializer, RoleSerializer, ModuleSerializer, RolePermissionSerializer, BranchSerializer
from app113209.utils import record_history
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render

from rest_framework.views import APIView

logger = logging.getLogger(__name__)
User = get_user_model()
    
def send_verification_code_backend(request):
    email = request.GET.get('email')
    if not email:
        logger.error("電子郵件是必填項")
        return JsonResponse({'success': False, 'message': '電子郵件是必填項'}, status=400)

    try:
        verification_code = str(uuid.uuid4())[:6]
        expiry_time = timezone.now() + timedelta(minutes=5)
        user, created = User.objects.get_or_create(email=email, defaults={
            'verification_code': verification_code,
            'expiry_time': expiry_time
        })
        if not created:
            user.verification_code = verification_code
            user.expiry_time = expiry_time
            user.save()
        send_verification_email(email, verification_code)
        logger.info(f"驗證碼 {verification_code} 已發送到 {email}，有效期至 {expiry_time}")
        return JsonResponse({'success': True, 'message': '驗證碼已發送'})
    except Exception as e:
        logger.error(f"發送驗證碼到 {email} 失敗: {e}")
        return JsonResponse({'success': False, 'message': '發送驗證碼失敗,請重試'}, status=500)

def send_verification_email(email, verification_code):
    subject = '請驗證您的電子郵件'
    message = f'您的驗證碼是 {verification_code}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    try:
        send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        logger.error(f"發送驗證郵件到 {email} 失敗: {e}")
        return JsonResponse({'success': False, 'message': '發送驗證碼失敗,請重試'}, status=500)

def validate_verification_code_backend(request):
    email = request.GET.get('email')
    code = request.GET.get('code')
    if not email or not code:
        logger.error("電子郵件和驗證碼是必填項")
        return JsonResponse({'success': False, 'message': '電子郵件和驗證碼是必填項'}, status=400)

    try:
        user = User.objects.get(email=email, verification_code=code)
        if user.expiry_time < timezone.now():
            logger.warning(f"{email} 的驗證碼已於 {user.expiry_time} 過期")
            return JsonResponse({'success': False, 'message': '驗證碼已過期'}, status=400)
        logger.info(f"{email} 的驗證碼有效")
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        logger.error(f"{email} 的驗證碼無效")
        return JsonResponse({'success': False, 'message': '驗證碼無效'}, status=400)


@api_view(['POST'])
def record_login_history(request):
    user = request.user
    if user.is_authenticated:
        action = request.data.get('action', '登入成功')
        device_brand = request.data.get('device_brand', '未知')
        device_type = request.data.get('device_type', '未知')
        operation_result = 1  # 登入成功

        UserHistory.objects.create(
            user=user,
            action=action,
            timestamp=timezone.now(),
            device_brand=device_brand,
            device_type=device_type,
            operation_result=operation_result
        )
        return Response({'message': '歷史紀錄已保存'}, status=status.HTTP_201_CREATED)
    return Response({'error': '未授權'}, status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        logger.debug(f"收到更新使用者 ID 的請求: {kwargs.get('pk')}")
        return super().update(request, *args, **kwargs)

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.filter(is_deleted=False)
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        module_name = request.data.get('module_name')
        if module_name:
            Module.objects.create(name=module_name)
            return Response({'success': True})
        return Response({'success': False, 'message': '模組名稱為必填項'})

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.filter(is_deleted=False)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.debug('創建角色請求數據: %s', request.data)
        try:
            response = super().create(request, *args, **kwargs)
            logger.debug('角色創建成功: %s', response.data)
            return response
        except Exception as e:
            logger.error('創建角色時發生錯誤: %s', e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        role = self.get_object()
        role.is_active = not role.is_active
        role.save()
        record_history(request.user, f"管理員 {request.user.username} 切換了角色 {role.name} 的狀態為 {'啟用' if role.is_active else '停用'}")
        return Response({'success': True})

class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.filter(is_deleted=False)
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_user(request, user_id):
    try:
        user = User.objects.get(id=user_id, is_active=False)
        user.is_active = True
        user.save()

        # 發送郵件通知用戶其帳號已啟用
        send_mail(
            '您的帳號已啟用',
            '恭喜！您的帳號已經被管理員審核並啟用。',
            'leewesley527@gmail.com',a
            [user.email],
            fail_silently=False,
        )

        return JsonResponse({'success': True, 'message': '用戶帳號已成功啟用並發送通知郵件'}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_role(request):
    role_data = request.data.get('role', {})
    role_permission_data = request.data.get('role_permission', [])

    serializer = RoleSerializer(data=role_data)
    if serializer.is_valid():
        role = serializer.save()

        for perm_data in role_permission_data:
            RolePermission.objects.create(
                role=role,
                permission_name=perm_data.get('permission_name'),
                can_add=perm_data.get('can_add'),
                can_query=perm_data.get('can_query'),
                can_view=perm_data.get('can_view'),
                can_edit=perm_data.get('can_edit'),
                can_delete=perm_data.get('can_delete'),
                can_print=perm_data.get('can_print'),
                can_export=perm_data.get('can_export'),
                can_maintain=perm_data.get('can_maintain')
            )

        return Response({'success': True}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_deleted = True
        user.save()
        record_history(request.user, f"管理員 {request.user.username} 刪除用戶 {user.username}")
        return Response({'success': True}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_role(request, role_id):
    try:
        role = get_object_or_404(Role, id=role_id)
        role.is_deleted = True
        role.save()
        record_history(request.user, f"管理員 {request.user.username} 刪除角色 {role.name}")
        return JsonResponse({'success': True})
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Role not found'}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_module(request, module_id):
    try:
        module = Module.objects.get(id=module_id)
        module.is_deleted = True
        module.save()
        record_history(request.user, f"管理員 {request.user.username} 刪除模組 {module.name}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Module.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# 圖表權限設置
# backend/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class BranchListAPIView(APIView):
    def get(self, request):
        # 從資料庫中獲取所有分店資料
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SavePermissionsAPIView(APIView):
    def post(self, request):
        selected_branches = request.data.get('selected_branches', [])
        
        if not selected_branches:
            return Response({"error": "請選擇至少一個分店"}, status=status.HTTP_400_BAD_REQUEST)

        # 處理保存邏輯，例如將分店與用戶或角色進行綁定
        # 假設我們將選擇的分店與某個用戶/角色綁定
        # 這裡省略具體的邏輯，只是模擬返回
        return Response({"message": "權限設置已保存"}, status=status.HTTP_200_OK)

# 登出視圖
from django.contrib.auth import logout

def logout_view(request):
    logout(request)  # 清除 session
    return JsonResponse({'message': '成功登出'}, status=200)
