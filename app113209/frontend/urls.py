# app113209/frontend/urls.py
from django.urls import path
from . import views as frontend_views
from . import api_views

app_name = 'frontend'

urlpatterns = [
    path('login/', frontend_views.FrontendLoginView.as_view(), name='frontend-login'),
    path('register/', frontend_views.FrontendRegisterView.as_view(), name='frontend-register'),
    path('send-verification-code/', frontend_views.SendVerificationCodeView.as_view(), name='send-verification-code'),
    path('get-csrf-token/', frontend_views.csrf_token_view, name='get-csrf-token'),
    path('profile/', frontend_views.user_profile, name='user-profile'),
    # 其他 URL 配置
]
