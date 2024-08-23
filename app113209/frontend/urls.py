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
<<<<<<< HEAD
    path('manager_home/', frontend_views.ManagerHomeView.as_view(), name='manager-home'),
    # path('branch_manager_home/', frontend_views.BranchManagerHomeView.as_view(), name='branch-manager-home'),
    path('get-data/', get_data, name='get_data'), 
=======
    path('profile/', frontend_views.user_profile, name='user-profile'),
    path('check_login_status/', frontend_views.check_login_status, name='check_login_status'),
    path('history/', frontend_views.history_records, name='history_records'),  # 使用函數視圖
    path('changepassword/', frontend_views.changepassword, name='changepassword'),
    path('preferences/', frontend_views.user_preferences, name='user_preferences'),
>>>>>>> dda5c7e (change)
]
