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

class FindPasswordTokenView(APIView):
    permission_classes = [AllowAny]
    def get_object(self, request):
        data = request.data
        user = get_object_or_404(User, username=data['username'], phone=data['phone'])
        return user
    def get(self, request):
        return Response(data="None")
    def post(self, request):
        data = request.data
        user = self.get_object(request)
        passcode = get_object_or_404(SMSPassCode ,user=user).passcode
        if not passcode == data['passcode']:
            return Response({'Status':'Passcode Error'}, status=status.HTTP_400_BAD_REQUEST)
        token_tuple = Token.objects.all().get_or_create(user=user)
        token = token_tuple[0]
        token_empty = token_tuple[1]
        serializer = FindPasswordTokenSerializer(token)
        if token_empty:
            return Response('Error', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

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
            return Response({'status':'set password'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class SMSPasscodeView(APIView):
    permission_classes = [AllowAny]
    def get_object(self, request):
        data = request.data
        user = get_object_or_404(User, username=data['username'], phone=data['phone'])
        return user
    def get(self, request):
        return Response(data="None")
    def post(self, request):
        # 이 공간에서 Passcode를 생성 -> DB저장 -> SMS 송신이 이루어진다.
        pass

class RegisterFarmView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get_object(self, request):
        user = self.request.user
        return user
    def get(self, request):
        return Response(data="only post request" ,status = status.HTTP_400_BAD_REQUEST)
    def post(self, request):
        user = self.get_object(request)
        data = request.data # farn  모델 정보, gcg_id, extra_info
        extra_info = data.pop('extra_info')
        gcg_id = data.pop('gcg_id')
        farm = Farm.objects.create(user=user, **data)
        farm.save()
        gcg = Gcg.objects.create(farm=farm, serial_num=gcg_id)
        gcg.save()
        extra_info_list = extra_info.split('/')
        for i in extra_info_list:
            step1=i.split('.')
            control_g_name = int(step1[0])
            control_og_lm_id = step1[1]
            control_og_rm_id = step1[2]
            control_og_custom_name = step1[3]
            temp = ControlGroup.objects.get_or_create(gcg=gcg, name=control_g_name)
            control_group = temp[0]
            state = temp[1]
            if state:
                control_group.save()
            temp = ControlOpenOption.objects.get_or_create(control_group=control_group)
            control_open_option = temp[0]
            state = temp[1]
            if state:
                control_open_option.save()
            temp = ControlOpenGroup.objects.get_or_create(control_group=control_group, og_lm_id=control_og_lm_id, og_rm_id=control_og_rm_id, og_custom_name=control_og_custom_name)
            control_open_group = temp[0]
            state = temp[1]
            if state:
                control_open_group.save()
        serializer = FarmSerializer(farm)
        return Response(serializer.data, status=status.HTTP_200_OK)
# Create your views here.
