from django.urls import path, re_path
from . import views
from .views import KakaoLogin

urlpatterns = [
    path('rest-auth/kakao/', KakaoLogin.as_view(), name='kakao_login'),
]