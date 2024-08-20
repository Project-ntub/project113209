from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserPreference
import json

@csrf_exempt
def get_preferences(request):
    preferences = UserPreference.objects.first()  # 根據需求調整為特定用戶的偏好
    if preferences:
        data = {
            'fontsize': preferences.fontsize,
            'notificationSettings': preferences.notificationSettings,
            'autoLogin': preferences.autoLogin,
        }
    else:
        data = {}
    return JsonResponse(data)

@csrf_exempt
def update_preference(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        preferences, created = UserPreference.objects.get_or_create(user_id=1)  # 根據需求調整 user_id
        preferences.fontsize = data.get('fontsize', preferences.fontsize)
        preferences.notificationSettings = data.get('notificationSettings', preferences.notificationSettings)
        preferences.autoLogin = data.get('autoLogin', preferences.autoLogin)
        preferences.save()
        return JsonResponse({'status': 'success'})

@csrf_exempt
def add_preference(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_preference = UserPreference.objects.create(
            fontsize=data.get('fontsize', 'medium'),
            notificationSettings=data.get('notificationSettings', 'off'),
            autoLogin=data.get('autoLogin', 'off')
        )
        return JsonResponse({'status': 'success', 'user_id': new_preference.user_id})

@csrf_exempt
def delete_preference(request):
    UserPreference.objects.all().delete()
    return JsonResponse({'status': 'success'})

@csrf_exempt
def query_preferences(request):
    fontsize = request.GET.get('fontsize')
    notificationSettings = request.GET.get('notificationSettings')
    autoLogin = request.GET.get('autoLogin')

    preferences = UserPreference.objects.all()

    if fontsize:
        preferences = preferences.filter(fontsize=fontsize)
    if notificationSettings:
        preferences = preferences.filter(notificationSettings=notificationSettings)
    if autoLogin:
        preferences = preferences.filter(autoLogin=autoLogin)

    results = list(preferences.values())

    return JsonResponse(results, safe=False)
