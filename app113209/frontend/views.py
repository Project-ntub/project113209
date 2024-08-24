from django.contrib.auth import authenticate, login
import json
import random
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
import json
import logging
import random
import re
import string
from django.views.generic import TemplateView
from app113209.models import User
# login
from django.contrib.auth.hashers import check_password, make_password
import re
import string
from django.views.generic import TemplateView

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


@login_required
@api_view(['GET'])
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

# 登錄
class FrontendLoginView(View):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        print("進入 post 方法")
        try:
            data = json.loads(request.body)
            print("收到的數據: ", data)
            email = data.get('email')
            password = data.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                print("驗證成功, 用戶: ", user.email)
                login(request, user)
                # 返回用户信息
                return JsonResponse({
                    'success': True,
                    'message': '登录成功',
                    'position': user.position_id,
                    'branch_id': user.branch_id
                }, status=200)
            else:
                print("驗證失敗")
                return JsonResponse({'success': False, 'message': '登录失败，请检查您的电子邮件和密码'}, status=400)
        except json.JSONDecodeError as e:
            print("JSON解析錯誤: ", e)
            return JsonResponse({'success': False, 'message': '无效的数据格式'}, status=400)
        except Exception as e:
            print("未預期的錯誤: ", e)
            return JsonResponse({'success': False, 'message': '服务器错误，请稍后再试'}, status=500)




from django.shortcuts import render

class HomePageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'frontend/home.html')

class ManagerHomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'frontend/manager_home.html')

class BranchManagerHomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'frontend/branch_home.html')

# 忘記密碼
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

# 重置密碼
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
    

# 過濾數據
from django.contrib.auth.decorators import login_required
from app113209.models import DataModel  # 假設有一個 DataModel 存儲數據

@login_required
def get_data(request):
    user = request.user

    # 如果用戶是店長
    if user.position_id == '店長':
        data = DataModel.objects.filter(branch_id=user.branch_id)
    elif user.position_id == '經理':
        data = DataModel.objects.all()
    else:
        return JsonResponse({'error': '未授權的訪問'}, status=403)
    
    data_list = list(data.values())  # 將數據轉為列表格式
    return JsonResponse(data_list, safe=False)
