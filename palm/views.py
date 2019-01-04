from django.shortcuts import render, get_object_or_404
from rest_framework import status, views
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
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
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(username=self.request.user)
        return qs

class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs

#class FindUserPasswordView(APIView):
#    permission_classes = [AllowAny]
#    def get(self, request, format=None):
#        #username='a'
#        #phone='b'
#        #data = {'username':username, 'phone':phone}
#        serializer = FindUserPasswordSerializer(data=request.data)
#        serializer.is_valid()
#        return Response(serializer.validated_data)
#    def post(self, request, *args, **kwargs):
#        serializer = FindUserPasswordSerializer(data=request.data)
#        serializer.is_valid()
#        #username= serializer.validated_data.get("username")
#        #phone = serializer.validated_data.get("phone")
#        #self.object = get_object_or_404(User, username=username, phone=phone)
#        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class FindPasswordTokenView(APIView):
    permission_classes = [AllowAny]
    def get_object(self, request):
        data = request.data
        user = get_object_or_404(User, username=data['username'], phone=data['phone'])
        token = Token.objects.get_or_create(user = user)[0]
        return token
    def get(self, request):
        return Response(data="None")
    def post(self, request):
        token = self.get_object(request)
        token_key = {'key':token.key}
        serializer = FindPasswordTokenSerializer(token, data=token_key)
        if not serializer.is_valid():
            return Response('Error', status=404)
        else:
            return Response(serializer.data, status=200)

class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.data.get('old_password')
            if not self.object.check_password(old_password):
                return Response({'old_password':['Wrong password']},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetPasswordAtFindView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response({'set_password_status':'set password'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Create your views here.
