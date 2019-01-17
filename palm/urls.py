from django.urls import path, re_path, include
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
# user 정보 조회를 위한 url 및 view
router.register('user', UserViewSet)
# farm 정보 조회를 위한 url 및 view
router.register('farm', FarmViewSet)
app_name = 'palm'
urlpatterns = [
    path('', include(router.urls)),
    # 비밀번호 및 아이디찾기를 위한 url 및 view
    path('sms-api/', SMSPasscodeView.as_view()),  # sms 인증을 위한 url 및 view
    path('find-password/', FindPasswordTokenView.as_view()),  # 비밀번호 찾기를 위한 url 및 view
    path('find-set-password/', SetPasswordAtFindView.as_view()),  # 비밀번호 찾기 후 비밀번호 재설정을 위한 url 및 view
    # 비밀번호 변경을 위한 url 및 view
    path('set-password/', SetPasswordView.as_view()),  # 비밀번호 변경을 위한 url 및 view
    # 농장 등록을 위한 url 및 view
    path('farm-register/', RegisterFarmView.as_view()),
    # 센싱데이터 조회를 위한 url 및 view
    path('sensor-value/', SensorValueView.as_view()),
    # 각 농장마다 동의 개수가 몇개인지 반환하는 url 및 view
    path('farm-num/', FarmNumberView.as_view()),
    # 날씨데이터 조회를 위한 url 및 view
    path('weather-value/', WeatherValueView.as_view()),
    # Gcg -> Server 에서 protocol 처리를 위한 url 및 view
    path('protocol-processing/<str:protocol>/', ProtocolView.as_view()),
]