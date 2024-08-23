# project113209\urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# import two_factor.urls
from django.shortcuts import redirect
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('/frontend/login/')), 
    # path('api/', include('app113209.backend.api_urls')),
    path('frontend/', include('app113209.frontend.urls', namespace='frontend')),
    path('backend/', include('app113209.backend.urls', namespace='backend')),
    # path('account/', include((two_factor.urls, 'two_factor'), namespace='two_factor')),
    path('api/frontend/', include('app113209.frontend.urls', namespace='frontend')),
    path('api/backend/', include('app113209.backend.api_urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]
                                      