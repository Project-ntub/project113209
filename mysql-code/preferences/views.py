from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import userpreferences
import json
import logging

# 設置日誌記錄器
logger = logging.getLogger(__name__)

@csrf_exempt
def get_preferences(request):
    if request.method == 'GET':
        try:
            preferences = userpreferences.objects.first()  # 假設只有一組偏好設定
            if preferences:
                data = {
                    'user_id': preferences.user_id,
                    'fontsize': preferences.fontsize,
                    'notificationSettings': preferences.notificationSettings,
                    'autoLogin': preferences.autoLogin,
                    'authentication': preferences.authentication
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'error': 'No preferences found'}, status=404)
        except Exception as e:
            logger.error(f"Error fetching preferences: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
def update_preference(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            preferences = userpreferences.objects.get(user_id=data['user_id'])
            preferences.fontsize = data['fontsize']
            preferences.notificationSettings = data['notificationSettings']
            preferences.autoLogin = data['autoLogin']
            preferences.authentication = data['authentication']
            preferences.save()
            return JsonResponse({'status': 'success'}, status=200)
        except userpreferences.DoesNotExist:
            logger.error("Preferences not found for update")
            return JsonResponse({'error': 'Preferences not found'}, status=404)
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
def add_preference(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_preference = userpreferences(
                fontsize=data['fontsize'],
                notificationSettings=data['notificationSettings'],
                autoLogin=data['autoLogin'],
                authentication=data['authentication']
            )
            new_preference.save()
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            logger.error(f"Error adding preference: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
def delete_preference(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            preferences = userpreferences.objects.get(user_id=data['user_id'])
            preferences.delete()
            return JsonResponse({'status': 'success'}, status=200)
        except userpreferences.DoesNotExist:
            logger.error("Preferences not found for deletion")
            return JsonResponse({'error': 'Preferences not found'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting preference: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
