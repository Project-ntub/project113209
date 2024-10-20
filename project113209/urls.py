# project113209\urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# import two_factor.urls
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings
from app113209.backend import api_views


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', lambda request: redirect('/frontend/login/')), 
    path('frontend/', include('app113209.frontend.urls', namespace='frontend')),
    path('backend/', include('app113209.backend.urls', namespace='backend')),
    path('api/frontend/', include('app113209.frontend.api_urls')),
    path('api/backend/', include('app113209.backend.api_urls')),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Vue.js will handle all paths starting from here
    path('', TemplateView.as_view(template_name='index.html'), name='frontend'),
   
]


