# app113209/frontend/urls.py

from django.urls import path
from . import views as frontend_views
from .views import get_data  

app_name = 'frontend'

urlpatterns = [
    path('login/', frontend_views.FrontendLoginView.as_view(), name='frontend-login'),
    path('register/', frontend_views.FrontendRegisterView.as_view(), name='frontend-register'),
    path('send-verification-code/', frontend_views.SendVerificationCodeView.as_view(), name='send-verification-code'),
    path('home/', frontend_views.HomePageView.as_view(), name='frontend-home'),  
    path('forgot-password/', frontend_views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', frontend_views.ResetPasswordView.as_view(), name='reset-password'),
    path('manager_home/', frontend_views.ManagerHomeView.as_view(), name='manager-home'),
    path('branch_home/', frontend_views.BranchManagerHomeView.as_view(), name='branch-home'),
    path('get-data/', get_data, name='get_data'), 
]
