# app113209\frontend\views.py
import logging
import json
import random
import re
import string
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
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
from app113209.models import User, UserPreferences  # 確保此模型存在
from app113209.models import HistoryRecord
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth import logout

# 日誌設定
logger = logging.getLogger(__name__)
from django.contrib.auth import login
# from django.contrib.auth.models import User

from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


from django.db.models import Q

# app113209/frontend/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app113209.models import CalendarEvent
import json

# 獲取日曆事件
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app113209.models import CalendarEvent
import json

# 獲取日曆事件的視圖，處理 GET 請求
# def get_calendar_events(request):
#     if request.method == 'GET':
#         try:
#             events = CalendarEvent.objects.all() 
#             event_list = [
#                 {
#                     "id": event.id,
#                     "title": event.title,
#                     "start": event.start.isoformat(), 
#                     "end": event.end.isoformat(),
#                     "description": event.description,
#                 }
#                 for event in events
#             ]
#             return JsonResponse(event_list, safe=False)  
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Method not allowed'}, status=405)

# 新增事件的視圖
# @csrf_exempt 
# def add_calendar_event(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             new_event = CalendarEvent.objects.create(
#                 title=data.get('title'),
#                 start=data.get('start'),
#                 end=data.get('end'),
#                 description=data.get('description', '')
#             )
#             return JsonResponse({
#                 "id": new_event.id,
#                 "title": new_event.title,
#                 "start": new_event.start.isoformat(),
#                 "end": new_event.end.isoformat(),
#                 "description": new_event.description,
#             }, status=201)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
#     return JsonResponse({'error': 'Method not allowed'}, status=405)


# @csrf_exempt
# def update_calendar_event(request, event_id):
#     if request.method == 'PUT':
#         data = json.loads(request.body)
#         try:
#             event = CalendarEvent.objects.get(id=event_id)
#             serializer = CalendarEventSerializer(event, data=data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return JsonResponse({'message': 'Event updated successfully!', 'event': serializer.data})
#             return JsonResponse({'error': serializer.errors}, status=400)
#         except CalendarEvent.DoesNotExist:
#             return JsonResponse({'error': 'Event not found'}, status=404)
#     return JsonResponse({'error': 'Invalid request method'}, status=400)

# @csrf_exempt
# def delete_calendar_event(request, event_id):
#     if request.method == 'DELETE':
#         try:
#             event = CalendarEvent.objects.get(id=event_id)
#             event.delete()
#             return JsonResponse({'message': 'Event deleted successfully!'})
#         except CalendarEvent.DoesNotExist:
#             return JsonResponse({'error': 'Event not found'}, status=404)
#     return JsonResponse({'error': 'Invalid request method'}, status=400)



User = get_user_model()
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def changepassword(request):
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        user = request.user

        # 確認輸入的當前密碼是否正確
        if not user.check_password(current_password):
            return JsonResponse({'message': '當前密碼不正確'}, status=400)

        # 確認一個月內是否已經更改過兩次密碼
        one_month_ago = timezone.now() - timezone.timedelta(days=30)
        password_changes = user.histories.filter(action='改密碼', timestamp__gte=one_month_ago).count()

        if password_changes >= 2:
            return JsonResponse({'message': '一個月內只能修改兩次密碼'}, status=400)

        # 驗證新密碼強度
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', new_password):
            return JsonResponse({'message': '新密碼不符合要求。密碼必須包含至少8個字符，且包括大小寫字母、數字和特殊字符。'}, status=400)

        # 修改密碼
        user.set_password(new_password)
        user.save()

        # 更新 session 以防止登出
        update_session_auth_hash(request, user)

        # 記錄密碼修改行為到歷史記錄
        user.histories.create(action='改密碼')

        return JsonResponse({'message': '密碼已成功修改'}, status=200)

    except Exception as e:
        return JsonResponse({'message': f'發生錯誤: {str(e)}'}, status=500)


@login_required
def user_preferences_view(request):
    user = request.user

    # 確保為新用戶創建偏好
    preferences, created = UserPreferences.objects.get_or_create(user=user)

    if request.method == 'GET':
        data = {
            'fontsize': preferences.fontsize,
            'notificationSettings': preferences.notificationSettings,
            'authentication': preferences.authentication
        }
        return JsonResponse(data)

    if request.method == 'POST':
        fontsize = request.POST.get('fontsize', 'medium')
        notificationSettings = request.POST.get('notificationSettings', '0') == '1'
        authentication = request.POST.get('authentication', '0') == '1'

        preferences.fontsize = fontsize
        preferences.notificationSettings = notificationSettings
        preferences.authentication = authentication
        preferences.save()

        return JsonResponse({'status': 'success'})

    





# 發送驗證碼
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
# 匯出圖表
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import io
from openpyxl import Workbook

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="chart.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Your Chart Data Here")
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def export_excel(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="chart.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Chart Data"

    data = [["Month", "Sales"], ["Jan", 40], ["Feb", 30], ["Mar", 20]]  # Example data
    for row in data:
        ws.append(row)

    output = io.BytesIO()
    wb.save(output)
    response.write(output.getvalue())
    return response

# 註冊
User = get_user_model()

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
            is_approved = False  # 用戶需要審核

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

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone=phone,
                is_active=False  # 註冊時設為不啟用
            )
            user.save()

            cache.delete(email)

            send_mail(
            '您的帳號已啟用',
            '恭喜！您的帳號已經被管理員審核並啟用。',
            'leewesley527@gmail.com',
            [user.email],
            fail_silently=False,
        )

            return JsonResponse({'success': True, 'message': '註冊成功！請等待管理員審核您的帳號。'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '無效的數據格式'}, status=400)

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        response = JsonResponse({'csrfToken': csrf_token})
        response.set_cookie('csrftoken', csrf_token)
        return response

# 登入
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class FrontendLoginView(View):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        print("進入 post 方法")
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)

                #用戶訊息
                print("\n===== 用户信息开始 =====")
                print("用户名:", user.username)
                print("电子邮件:", user.email)
                print("电话号码:", user.phone)
                print("职位 ID:", user.position_id)
                print("分店 ID:", user.branch_id)
                print("是否活跃:", user.is_active)
                print("是否已验证:", user.is_verified)
                print("是否已批准:", user.is_approved)
                print("部门 ID:", user.department_id)
                print("性别:", user.gender)
                print("加入日期:", user.date_joined)
                print("===== 用户信息结束 =====\n")

                # 返回登入成功
                return JsonResponse({
                    'success': True,
                    'message': '登录成功',
                    'position': user.position_id,
                    'branch_id': user.branch_id
                }, status=200)
            else:
                return JsonResponse({'success': False, 'message': '登入失敗，請檢查您的電子郵件和密碼'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '資料格式無效'}, status=400)




def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # 設置 session
            print(f"User {user.username} has logged in successfully.")  # 添加日誌輸出
            return JsonResponse({'success': True, 'message': 'Login successful'})
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')
# 獲取歷史記錄的視圖
def history_records(request):
    if request.method == 'GET':
        history = HistoryRecord.objects.filter(user=request.user).values('id', 'action_time', 'action_description', 'additional_info')
        return JsonResponse(list(history), safe=False)

@login_required
def history_detail(request, id):
    try:
        history = HistoryRecord.objects.get(id=id, user=request.user)
        detail = {
            'id': history.id,
            'action': history.action_description,
            'timestamp': history.action_time,
            'user': history.user.username,
            'device': {
                'brand': history.device_brand,
                'type': history.device_type
            } if hasattr(history, 'device_brand') and hasattr(history, 'device_type') else None,
            'success': history.success if hasattr(history, 'success') else None,
        }
        return JsonResponse(detail)
    except HistoryRecord.DoesNotExist:
        return JsonResponse({'error': '未找到該紀錄的詳細信息。'}, status=404)
@login_required
def check_login_status(request):
    return JsonResponse({'loggedIn': request.user.is_authenticated})

# 首頁
class HomePageView(TemplateView):
    template_name = "frontend/home.html"
# View for ManagerHome
class ManagerHomeView(TemplateView):
    template_name = "frontend/manager_home.html"

# View for BranchManagerHome
class BranchManagerHomeView(TemplateView):
    template_name = "frontend/branch_manager_home.html"
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

# 更改密码视图
# @csrf_exempt
# @login_required
# def changepassword(request):
#     try:
#         if request.method == 'POST':
#             data = json.loads(request.body)
#             current_password = data.get('current_password')
#             new_password = data.get('new_password')

#             user = request.user

#             if user.is_locked:
#                 return JsonResponse({'message': '帳號已被鎖定，請聯絡管理員'}, status=403)

#             if not user.check_password(current_password):
#                 user.failed_attempts += 1
#                 if user.failed_attempts >= 3:
#                     user.is_locked = True
#                     user.save()
#                     return JsonResponse({'message': '帳號已被鎖定，請聯絡管理員'}, status=403)
#                 user.save()
#                 return JsonResponse({'message': '當前密碼錯誤'}, status=400)

#             user.failed_attempts = 0
#             user.set_password(new_password)
#             user.save()

#             logout(request)
#             return JsonResponse({'message': '密碼修改成功，已登出'}, status=200)

#         else:
#             return JsonResponse({'message': '僅支援POST請求'}, status=405)

#     except PermissionDenied:
#         return JsonResponse({'message': '未授權，跳過該錯誤'}, status=401)
    
#     except ObjectDoesNotExist:
#         return JsonResponse({'message': '資源未找到，跳過該錯誤'}, status=404)
    
#     except Exception as e:
#         return JsonResponse({'message': f'其他錯誤: {str(e)}'}, status=500)

@api_view(['GET', 'PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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

# 過濾數據

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
# logout


def logout_view(request):
    logout(request)  # 清除 session
    return JsonResponse({'message': '成功登出'}, status=200)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar_events(request):
    try:
        events = CalendarEvent.objects.filter(user=request.user)
        event_list = [
            {
                "id": event.id,
                "title": event.title or "未命名事件",
                "start": event.start.isoformat() if event.start else None,
                "end": event.end.isoformat() if event.end else None,
                "description": event.description or "",
                "privacy": event.privacy or "public",
            }
            for event in events if event.start and event.end
        ]
        print("後端返回的事件：", event_list)  # 調試輸出
        return Response(event_list, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_calendar_event(request, event_id):
    try:
        event = CalendarEvent.objects.get(id=event_id, user=request.user)
        data = request.data

        # 確保 start 和 end 的數據正確並轉換為 datetime
        start = data.get('start')
        end = data.get('end')
        if start:
            event.start = datetime.fromisoformat(start)
        if end:
            event.end = datetime.fromisoformat(end)

        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)
        event.save()
        return Response({
            "id": event.id,
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat(),
            "description": event.description,
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'error': f'日期格式錯誤: {str(e)}'}, status=400)
    except CalendarEvent.DoesNotExist:
        return Response({'error': '事件不存在或無權限'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



# 新增事件的視圖
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_calendar_event(request):
    if request.method == 'POST':
        try:
            data = request.data  # 確保使用 DRF 的 request.data
            # 解析日期時間字串為 datetime 物件
            start = datetime.fromisoformat(data.get('start'))
            end = datetime.fromisoformat(data.get('end'))

            # 新增事件
            new_event = CalendarEvent.objects.create(
                user=request.user,
                title=data.get('title'),
                start=start,
                end=end,
                description=data.get('description', ''),
                privacy=data.get('privacy', 'public'),
            )

            # 回傳成功的事件資料
            return Response({
                "id": new_event.id,
                "title": new_event.title,
                "start": new_event.start.isoformat(),
                "end": new_event.end.isoformat(),
                "description": new_event.description,
                "privacy": new_event.privacy,
            }, status=201)
        except ValueError as e:
            return Response({'error': f'日期格式錯誤: {str(e)}'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    return Response({'error': 'Method not allowed'}, status=405)

# 刪除事件的視圖
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_calendar_event(request, event_id):
    try:
        event = CalendarEvent.objects.get(id=event_id, user=request.user)
        event.delete()
        return Response({'message': '事件刪除成功！'}, status=status.HTTP_200_OK)
    except CalendarEvent.DoesNotExist:
        return Response({'error': '事件不存在或無權限'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)