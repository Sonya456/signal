from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



from django.urls import path
from . import views

urlpatterns = [

    # FRONTEND PAGES
    path('', views.home, name='home'),
    path('login/', views.frontend_login, name='login'),
    path('register/', views.frontend_register, name='register'),
    path('profile/', views.profile_page, name='profile'),
    path('', views.home, name='home'),

    path('api/volume/', views.volume_signal),
    path('api/trend/', views.trend_filter),
    path('api/distance/', views.resistance_distance),
    path('api/rsi/', views.rsi_signal),
    path('api/breakout/', views.breakout_signal),
    path('api/structure/', views.market_structure),
    path('api/support/', views.support_reaction),
    path('api/score/', views.long_score),
    path('api/price/', views.live_price),


    # JWT API
    path('api/register/', views.register_api, name='api_register'),
    path('api/login/', views.login_api, name='api_login'),
    path('api/logout/', views.logout_api, name='api_logout'),
    path('api/protected/', views.protected_api, name='api_protected'),
]