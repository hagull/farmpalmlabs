from .models import SensorInfoOrValue
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from accounts.models import User
from .models import Farm
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token

class SensorInfoOrValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorInfoOrValue
        fields = '__all__'
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
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