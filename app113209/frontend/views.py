from django.contrib.auth import authenticate, login
import json
import random
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from app113209.models import User
# login
from django.views.generic import TemplateView
# forgetpassword
import string
# resetpassword
from django.contrib.auth.hashers import make_password
@method_decorator(csrf_exempt, name='dispatch')
class SendVerificationCodeView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'success': False, 'message': '電子郵件地址不能為空'}, status=400)

            # 生成6位數的驗證碼
            verification_code = random.randint(100000, 999999)

            # 將驗證碼存儲在緩存中，有效期為5分鐘
            cache.set(email, verification_code, timeout=300)

            # 發送電子郵件
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

@login_required
def check_login_status(request):
    return JsonResponse({'loggedIn': True})

@login_required
def get_history(request):
    # 假設這裡有一些歷史記錄，這些記錄可能從數據庫中取得
    history = [
        {'id': 1, 'date': '2024/1/22 16:22:39', 'action': '編輯個人資訊', 'user': 'User1'},
        {'id': 2, 'date': '2024/1/22 16:00:21', 'action': '查看首頁', 'user': 'User2'},
        {'id': 3, 'date': '2024/1/28 16:00:21', 'action': '修改密碼', 'user': 'User2'},
        {'id': 4, 'date': '2023/12/28 16:00:21', 'action': '忘記密碼', 'user': 'User2'},
    ]
    return JsonResponse(history, safe=False)

# register
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
            data = json.loads(request.body)
            print("Received data:", data)  # 打印收到的数据

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
            # 檢查電話號碼是否已經被使用
            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'success': False, 'message': '電話號碼已經被使用'}, status=400)
            user = User.objects.create_user(username=username, email=email, password=password,phone=phone)
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

# login
class FrontendLoginView(View):
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
                return JsonResponse({'success': False, 'message': '用戶名或密碼錯誤'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        response = JsonResponse({'csrfToken': csrf_token})
        response.set_cookie('csrftoken', csrf_token)
        return response
# homepage
class HomePageView(TemplateView):
    template_name = "frontend/home.html"
#  forgetpassword
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

            # 生成一个随机密码重置代码
            reset_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            cache.set(reset_code, email, timeout=180)
            # 在这里你可以将密码重置代码存储在数据库或缓存中
            # 并发送到用户的电子邮件
            send_mail(
                '您的密碼重置代碼',
                f'您的密碼重置代碼是：{reset_code}',
                'from@example.com',  # 发件人地址
                [email],
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': '密碼重置代碼已發送到您的電子郵件'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)
    
    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})
# resetpassword
@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            reset_code = data.get('resetCode')
            new_password = data.get('newPassword')
            
            # 从缓存中获取与重置代码对应的邮箱
            email = cache.get(reset_code)
            if not email:
                return JsonResponse({'success': False, 'message': '重置代碼無效或已過期'}, status=400)

            try:
                # 使用邮箱查找用户并更新密码
                user = User.objects.get(email=email)
                user.password = make_password(new_password)
                user.save()

                # 删除缓存中的重置代码
                cache.delete(reset_code)
                
                return JsonResponse({'success': True, 'message': '密碼重置成功！'}, status=200)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': '用戶不存在'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})
    
@api_view(['GET', 'PUT'])
def user_profile (request):
    if request.method == 'GET':
        user = request.user
        data = {
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "department_name": user.department_id,
            "position_name": user.position_id
        }
        return JsonResponse
    
    if request.method == "PUT":
        user = request.user
        data = json.loads(request.body)
        user.email = data.get("email", user.email)
        user.phone = data.get("phone", user.phone)
        user.department_id = data.get("department_id", user.department_id)
        user.position_id = data.get("position_id", user.position_id)
        user.save()
        return JsonResponse
    