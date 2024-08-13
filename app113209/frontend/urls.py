# app113209/frontend/urls.py

from django.urls import path
from . import views as frontend_views
from .views import csrf_token_view
app_name = 'frontend'

urlpatterns = [
    path('login/', frontend_views.FrontendLoginView.as_view(), name='frontend-login'),
    path('register/', frontend_views.FrontendRegisterView.as_view(), name='frontend-register'),
    path('send-verification-code/', frontend_views.SendVerificationCodeView.as_view(), name='send-verification-code'),
    path('get-csrf-token/', csrf_token_view, name='get-csrf-token'),
    # 其他 URL 配置
]
