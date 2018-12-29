from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Create your views here.
