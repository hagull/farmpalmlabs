from rest_framework.serializers import ModelSerializer
from .models import SensorInfoOrValue
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from accounts.models import User
class SensorInfoOrValueSerializer(ModelSerializer):
    class Meta:
        model = SensorInfoOrValue
        fields = '__all__'
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'