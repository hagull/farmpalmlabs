from .models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from accounts.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token

# class SensorInfoOrValueSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SensorInfoOrValue
#         fields = '__all__'
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
class FarmSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Farm
        fields = '__all__'
class FindPasswordTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields=['key']

class SetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=False)
    new_password = serializers.CharField()
    def validate_new_password(self, value):
        validate_password(value)
        return value
# SMS 메세지 passcode 저장 및 송신을 위한 api
class SMSPasscodeSerializer(serializers.Serializer):
    username = serializers.CharField()
    phone = serializers.CharField()

class RegisterFarmSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    gcg_id = serializers.CharField(required=False)
    # 동의 번호( 1동 2동 3동 ... N동 ) + 개폐기 그룹의 번호 + 개폐기 그룹의 CustomName
    extra_info = serializers.CharField(required=False)
class SensorValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorInfoOrValue
        # fields = '__all__'
        fields = ['temp_mean', 'humd_mean', 'co2_mean', 'soil_temp_mean', 'soil_humd_mean','soil_ec_mean', 'culture_medium_temp_mean','nutrient_solution_ec_mean','nutrient_solution_ph_mean', 'test_date']
class WeatherValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherInfo
        fields = ['rain_value', 'temp_value', 'humd_value',
                  'wind_dir_value', 'wind_spd_value',
                  'test_date']