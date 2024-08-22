import logging
import json
import random
import re
import string
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.admin.models import LogEntry, CHANGE
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.decorators import api_view
from app113209.models import UserPreferences  # 確保此模型存在
from app113209.models import ActionHistory

# 日誌設定
logger = logging.getLogger(__name__)

# 发送验证码
@method_decorator(csrf_exempt, name='dispatch')
class SendVerificationCodeView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'success': False, 'message': '電子郵件地址不能為空'}, status=400)

            verification_code = random.randint(100000, 999999)
            cache.set(email, verification_code, timeout=300)

            send_mail(
                '您的驗證碼',
                f'您的驗證碼是 {verification_code}，有效期為5分鐘。',
                '911213sw@gmail.com',  # 發件人郵箱
                [email],
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': '驗證碼已發送'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)

# 注册
@method_decorator(csrf_exempt, name='dispatch')
class FrontendRegisterView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirmPassword')
            phone = data.get('phone')
            verification_code = data.get('verificationCode')

            if password != confirm_password:
                return JsonResponse({'success': False, 'message': '密碼和確認密碼不匹配'}, status=400)

            try:
                validate_password(password)
            except ValidationError as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=400)

            cached_verification_code = cache.get(email)
            if not cached_verification_code or str(cached_verification_code) != verification_code:
                return JsonResponse({'success': False, 'message': '驗證碼不正確或已過期'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': '用戶名已存在'}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': '電子郵件已被註冊'}, status=400)
            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'success': False, 'message': '電話號碼已經被使用'}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password, phone=phone)
            user.save()

            cache.delete(email)

            send_mail(
                '歡迎註冊',
                '感謝您的註冊！',
                'from@example.com',
                [email],
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': '註冊成功！'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        response = JsonResponse({'csrfToken': csrf_token})
        response.set_cookie('csrftoken', csrf_token)
        return response

# 登录视图
class FrontendLoginView(View):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'message': '登錄成功'}, status=200)
            else:
                return JsonResponse({'success': False, 'message': '登入失敗，請檢查您的電子郵件和密碼'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        response = JsonResponse({'csrfToken': csrf_token})
        response.set_cookie('csrftoken', csrf_token)
        return response

# 檢查登入狀態視圖
@login_required
def check_login_status(request):
    return JsonResponse({'loggedIn': True})
@login_required
@login_required
def get_history(request):
    logger.debug("get_history view called")
    user = request.user
    history_items = ActionHistory.objects.filter(user=user).order_by('-date')
    history_data = [
        {
            'id': item.id,
            'action': item.action,
            'changes': item.changes,
            'date': item.date.strftime('%Y-%m-%d %H:%M:%S'),
            'user': item.user.username,
        }
        for item in history_items
    ]
    logger.debug(f"History data: {history_data}")
    return JsonResponse({'history': history_data})
# 忘记密码视图
@method_decorator(csrf_exempt, name='dispatch')
class ForgotPasswordView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'success': False, 'message': '電子郵件地址不能為空'}, status=400)

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': '此電子郵件未註冊'}, status=404)

            reset_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            cache.set(reset_code, email, timeout=180)

            send_mail(
                '您的密碼重置代碼',
                f'您的密碼重置代碼是：{reset_code}',
                'from@example.com',
                [email],
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': '密碼重置代碼已發送到您的電子郵件'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})

# 重置密码视图
@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(View):
    def validate_password_strength(self, password):
        if (len(password) < 8 or
            not re.search(r'[A-Z]', password) or
            not re.search(r'[a-z]', password) or
            not re.search(r'\d', password) or
            not re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
            return False
        return True

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            reset_code = data.get('resetCode')
            new_password = data.get('newPassword')

            email = cache.get(reset_code)
            if not email:
                return JsonResponse({'success': False, 'message': '重置代碼無效或已過期'}, status=400)

            try:
                user = User.objects.get(email=email)

                if check_password(new_password, user.password):
                    return JsonResponse({'success': False, 'message': '新密碼不能與舊密碼相同'}, status=400)

                if not self.validate_password_strength(new_password):
                    return JsonResponse({'success': False, 'message': '密碼必須至少包含8個字符，且包括大小寫字母、數字和特殊字符'}, status=400)

                user.password = make_password(new_password)
                user.save()

                cache.delete(reset_code)

                return JsonResponse({'success': True, 'message': '密碼重置成功！'}, status=200)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': '用戶不存在'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})

# 更改密码视图
@login_required
@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            current_password = data.get('currentPassword')
            new_password = data.get('newPassword')

            user = request.user

            # 檢查當前密碼是否正確
            if not check_password(current_password, user.password):
                return JsonResponse({'success': False, 'message': '原密碼不正確'}, status=400)
            
            # 驗證新密碼的強度
            if len(new_password) < 8 or not re.search(r'[A-Z]', new_password) or not re.search(r'[a-z]', new_password) or not re.search(r'\d', new_password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                return JsonResponse({'success': False, 'message': '密碼必須至少包含8個字符，且包括大小寫字母、數字和特殊字符'}, status=400)

            # 檢查新密碼是否與舊密碼相同
            if check_password(new_password, user.password):
                return JsonResponse({'success': False, 'message': '新密碼不能與舊密碼相同'}, status=400)

            # 更新密碼
            user.password = make_password(new_password)
            user.save()

            # 記錄更改密碼的動作到歷史紀錄
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(User).pk,
                object_id=user.id,
                object_repr=str(user),
                action_flag=CHANGE,
                change_message="更改密碼"
            )
            
            return JsonResponse({
                'success': True, 
                'message': '密碼已成功修改',
                'username': user.username  # 回傳登入用戶名
            }, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)

        except Exception as e:
            return JsonResponse({'success': False, 'message': '服務器錯誤，請稍後再試'}, status=500)

    return JsonResponse({'success': False, 'message': '無效的請求方法'}, status=405)

# 用户信息视图
@api_view(['GET', 'PUT'])
def user_profile(request):
    if request.method == 'GET':
        user = request.user
        data = {
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "department_name": user.department_id,
            "position_name": user.position_id
        }
        return JsonResponse(data, safe=False)

    if request.method == "PUT":
        user = request.user
        data = json.loads(request.body)
        user.email = data.get("email", user.email)
        user.phone = data.get("phone", user.phone)
        user.department_id = data.get("department_id", user.department_id)
        user.position_id = data.get("position_id", user.position_id)
        user.save()
        return JsonResponse({'success': True, 'message': '資料更新成功'}, status=200)

# 获取和更新用户偏好设置视图
@api_view(['GET', 'POST'])
@csrf_exempt
def user_preferences(request):
    user = request.user
    if request.method == 'GET':
        try:
            preferences = UserPreferences.objects.get(user=user)
            data = {
                "fontSize": preferences.font_size,
                "notification": preferences.notifications_enabled,
                "autoLogin": preferences.auto_login_enabled,
                "authentication": preferences.authentication_enabled
            }
            return JsonResponse(data, safe=False)
        except UserPreferences.DoesNotExist:
            return JsonResponse({'error': 'Preferences not found'}, status=404)

    elif request.method == 'POST':
        data = json.loads(request.body)
        preferences, created = UserPreferences.objects.get_or_create(user=user)
        preferences.font_size = data.get('fontSize', preferences.font_size)
        preferences.notifications_enabled = data.get('notification', preferences.notifications_enabled)
        preferences.auto_login_enabled = data.get('autoLogin', preferences.auto_login_enabled)
        preferences.authentication_enabled = data.get('authentication', preferences.authentication_enabled)
        preferences.save()
        return JsonResponse({'success': True, 'message': 'Preferences updated successfully'})
    

class HomePageView(TemplateView):
    template_name = 'frontend/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 在这里添加上下文数据，例如：
        context['message'] = '欢迎来到主页'
        return context