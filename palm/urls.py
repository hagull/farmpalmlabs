from django.urls import path, re_path, include
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('user', UserViewSet)
router.register('farm', FarmViewSet)
router.register('sensor-value-viewset', SensorValueViewSet)
app_name = 'palm'
urlpatterns = [
    path('', include(router.urls)),
    path('find-password/', FindPasswordTokenView.as_view()),
    path('set-password/',SetPasswordView.as_view()),
    path('find-set-password/', SetPasswordAtFindView.as_view()),
    path('sms-api/', SMSPasscodeView.as_view()),
    path('farm-register/', RegisterFarmView.as_view()),
    path('sensor-value/', SensorValueView.as_view()),
    path('farm-num/', FarmNumber.as_view()),
    path('weather-value/', WeatherValueView.as_view()),
]