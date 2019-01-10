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
from statistics import mean

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
class SensorValueViewSet(viewsets.ModelViewSet):
    queryset = SensorInfoOrValue.objects.all()
    serializer_class = SensorValueSerializer
    permission_classes = [AllowAny]
class WeatherValueView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, request):
        data = request.data
        gcg_id = data['gcg_id']
        gcg = Gcg.objects.all().get(serial_num=gcg_id)
        weather_value = WeatherInfo.objects.filter(gcg=gcg).order_by('-test_date').first()
        return weather_value
    def post(self, request):
        weather_value = self.get_object(request)
        serializer = WeatherValueSerializer(weather_value)
        return Response(serializer.data, status=status.HTTP_200_OK)
class SensorValueView(APIView):
    permission_classes = [AllowAny]
    def get_queryset(self, request):
        # user = self.request.user 이 줄은 유저검증을 위한 항목
        data = request.data
        gcg_id = data['gcg_id']
        control_group_name = data['control_group_name']
        gcg = Gcg.objects.get(serial_num=gcg_id)
        control_group = ControlGroup.objects.get(gcg=gcg, name=control_group_name)
        sensor_value_qs = SensorInfoOrValue.objects.filter(control_group=control_group).order_by('-test_date')
        return sensor_value_qs
    def get(self, request):
        return Response(request.data, status=status.HTTP_200_OK)
    def post(self, request):
        data = []
        qs = self.get_queryset(request)
        extra_qs = qs[:288]
        value_qs = qs.filter(display_data=True)[:24]
        temp_value1_list = [i[0] for i in extra_qs.values_list('temp_value1')]
        temp_value2_list = [i[0] for i in extra_qs.values_list('temp_value2')]
        temp_value3_list = [i[0] for i in extra_qs.values_list('temp_value3')]

        humd_value1_list = [i[0] for i in extra_qs.values_list('humd_value1')]
        humd_value2_list = [i[0] for i in extra_qs.values_list('humd_value2')]
        humd_value3_list = [i[0] for i in extra_qs.values_list('humd_value3')]

        co2_value1_list = [i[0] for i in extra_qs.values_list('co2_value1')]
        co2_value2_list = [i[0] for i in extra_qs.values_list('co2_value2')]
        co2_value3_list = [i[0] for i in extra_qs.values_list('co2_value3')]

        soil_temp_value1_list = [i[0] for i in extra_qs.values_list('soil_temp_value1')]
        soil_temp_value2_list = [i[0] for i in extra_qs.values_list('soil_temp_value2')]
        soil_temp_value3_list = [i[0] for i in extra_qs.values_list('soil_temp_value3')]

        soil_humd_value1_list = [i[0] for i in extra_qs.values_list('soil_humd_value1')]
        soil_humd_value2_list = [i[0] for i in extra_qs.values_list('soil_humd_value2')]
        soil_humd_value3_list = [i[0] for i in extra_qs.values_list('soil_humd_value3')]

        soil_ec_value1_list = [i[0] for i in extra_qs.values_list('soil_ec_value1')]
        soil_ec_value2_list = [i[0] for i in extra_qs.values_list('soil_ec_value2')]
        soil_ec_value3_list = [i[0] for i in extra_qs.values_list('soil_ec_value3')]

        culture_medium_temp_value1_list = [i[0] for i in extra_qs.values_list('culture_medium_temp_value1')]
        culture_medium_temp_value2_list = [i[0] for i in extra_qs.values_list('culture_medium_temp_value2')]
        culture_medium_temp_value3_list = [i[0] for i in extra_qs.values_list('culture_medium_temp_value3')]

        nutrient_solution_ec_value1_list = [i[0] for i in extra_qs.values_list('nutrient_solution_ec_value1')]
        nutrient_solution_ec_value2_list = [i[0] for i in extra_qs.values_list('nutrient_solution_ec_value2')]
        nutrient_solution_ec_value3_list = [i[0] for i in extra_qs.values_list('nutrient_solution_ec_value3')]

        nutrient_solution_ph_value1_list = [i[0] for i in extra_qs.values_list('nutrient_solution_ph_value1')]
        nutrient_solution_ph_value2_list = [i[0] for i in extra_qs.values_list('nutrient_solution_ph_value2')]
        nutrient_solution_ph_value3_list = [i[0] for i in extra_qs.values_list('nutrient_solution_ph_value3')]

        value_max_min_mean = {
            'temp_value1_max': max(temp_value1_list),
            'temp_value1_max_date':extra_qs[temp_value1_list.index(max(temp_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'temp_value1_min': min(temp_value1_list),
            'temp_value1_min_date':extra_qs[temp_value1_list.index(min(temp_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'temp_value1_mean': mean(temp_value1_list),

            'temp_value2_max': max(temp_value2_list),
            'temp_value2_max_date': extra_qs[temp_value2_list.index(max(temp_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'temp_value2_min': min(temp_value2_list),
            'temp_value2_min_date': extra_qs[temp_value2_list.index(min(temp_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'temp_value2_mean': mean(temp_value2_list),

            'temp_value3_max': max(temp_value3_list),
            'temp_value3_max_date': extra_qs[temp_value3_list.index(max(temp_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'temp_value3_min': min(temp_value3_list),
            'temp_value3_min_date': extra_qs[temp_value3_list.index(min(temp_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'temp_value3_mean': mean(temp_value3_list),

            'humd_value1_max': max(humd_value1_list),
            'humd_value1_max_date': extra_qs[humd_value1_list.index(max(humd_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'humd_value1_min': min(humd_value1_list),
            'humd_value1_min_date': extra_qs[humd_value1_list.index(min(humd_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'humd_value1_mean': mean(humd_value1_list),

            'humd_value2_max': max(humd_value2_list),
            'humd_value2_max_date': extra_qs[humd_value2_list.index(max(humd_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'humd_value2_min': min(humd_value2_list),
            'humd_value2_min_date': extra_qs[humd_value2_list.index(min(humd_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'humd_value2_mean': mean(humd_value2_list),

            'humd_value3_max': max(humd_value3_list),
            'humd_value3_max_date': extra_qs[humd_value3_list.index(max(humd_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'humd_value3_min': min(humd_value3_list),
            'humd_value3_min_date': extra_qs[humd_value3_list.index(min(humd_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'humd_value3_mean': mean(humd_value3_list),

            'co2_value1_max': max(co2_value1_list),
            'co2_value1_max_date': extra_qs[co2_value1_list.index(max(co2_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'co2_value1_min': min(co2_value1_list),
            'co2_value1_min_date': extra_qs[co2_value1_list.index(min(co2_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'co2_value1_mean': mean(co2_value1_list),

            'co2_value2_max': max(co2_value2_list),
            'co2_value2_max_date': extra_qs[co2_value2_list.index(max(co2_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'co2_value2_min': min(co2_value2_list),
            'co2_value2_min_date': extra_qs[co2_value2_list.index(min(co2_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'co2_value2_mean': mean(co2_value2_list),

            'co2_value3_max': max(co2_value3_list),
            'co2_value3_max_date': extra_qs[co2_value3_list.index(max(co2_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'co2_value3_min': min(co2_value3_list),
            'co2_value3_min_date': extra_qs[co2_value3_list.index(min(co2_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'co2_value3_mean': mean(co2_value3_list),

            'soil_temp_value1_max': max(soil_temp_value1_list),
            'soil_temp_value1_max_date': extra_qs[soil_temp_value1_list.index(max(soil_temp_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_temp_value1_min': min(soil_temp_value1_list),
            'soil_temp_value1_min_date': extra_qs[soil_temp_value1_list.index(min(soil_temp_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_temp_value1_mean': mean(soil_temp_value1_list),

            'soil_temp_value2_max': max(soil_temp_value2_list),
            'soil_temp_value2_max_date': extra_qs[
                soil_temp_value2_list.index(max(soil_temp_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_temp_value2_min': min(soil_temp_value2_list),
            'soil_temp_value2_min_date': extra_qs[
                soil_temp_value2_list.index(min(soil_temp_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_temp_value2_mean': mean(soil_temp_value2_list),

            'soil_temp_value3_max': max(soil_temp_value3_list),
            'soil_temp_value3_max_date': extra_qs[
                soil_temp_value3_list.index(max(soil_temp_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_temp_value3_min': min(soil_temp_value3_list),
            'soil_temp_value3_min_date': extra_qs[
                soil_temp_value3_list.index(min(soil_temp_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_temp_value3_mean': mean(soil_temp_value3_list),

            'soil_humd_value1_max': max(soil_humd_value1_list),
            'soil_humd_value1_max_date': extra_qs[soil_humd_value1_list.index(max(soil_humd_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_humd_value1_min': min(soil_humd_value1_list),
            'soil_humd_value1_min_date': extra_qs[soil_humd_value1_list.index(min(soil_humd_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_humd_value1_mean': mean(soil_humd_value1_list),

            'soil_humd_value2_max': max(soil_humd_value2_list),
            'soil_humd_value2_max_date': extra_qs[
                soil_humd_value2_list.index(max(soil_humd_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_humd_value2_min': min(soil_humd_value2_list),
            'soil_humd_value2_min_date': extra_qs[
                soil_humd_value2_list.index(min(soil_humd_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_humd_value2_mean': mean(soil_humd_value2_list),

            'soil_humd_value3_max': max(soil_humd_value3_list),
            'soil_humd_value3_max_date': extra_qs[
                soil_humd_value3_list.index(max(soil_humd_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_humd_value3_min': min(soil_humd_value3_list),
            'soil_humd_value3_min_date': extra_qs[
                soil_humd_value3_list.index(min(soil_humd_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_humd_value3_mean': mean(soil_humd_value3_list),

            'soil_ec_value1_max': max(soil_ec_value1_list),
            'soil_ec_value1_max_date': extra_qs[soil_ec_value1_list.index(max(soil_ec_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_ec_value1_min': min(soil_ec_value1_list),
            'soil_ec_value1_min_date': extra_qs[soil_ec_value1_list.index(min(soil_ec_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_ec_value1_mean': mean(soil_ec_value1_list),

            'soil_ec_value2_max': max(soil_ec_value2_list),
            'soil_ec_value2_max_date': extra_qs[soil_ec_value2_list.index(max(soil_ec_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_ec_value2_min': min(soil_ec_value2_list),
            'soil_ec_value2_min_date': extra_qs[soil_ec_value2_list.index(min(soil_ec_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_ec_value2_mean': mean(soil_ec_value2_list),

            'soil_ec_value3_max': max(soil_ec_value3_list),
            'soil_ec_value3_max_date': extra_qs[soil_ec_value3_list.index(max(soil_ec_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_ec_value3_min': min(soil_ec_value3_list),
            'soil_ec_value3_min_date': extra_qs[soil_ec_value3_list.index(min(soil_ec_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'soil_ec_value3_mean': mean(soil_ec_value3_list),

            'culture_medium_temp_value1_max': max(culture_medium_temp_value1_list),
            'culture_medium_temp_value1_max_date': extra_qs[culture_medium_temp_value1_list.index(max(culture_medium_temp_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'culture_medium_temp_value1_min': min(culture_medium_temp_value1_list),
            'culture_medium_temp_value1_min_date': extra_qs[culture_medium_temp_value1_list.index(min(culture_medium_temp_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'culture_medium_temp_value1_mean': mean(culture_medium_temp_value1_list),

            'culture_medium_temp_value2_max': max(culture_medium_temp_value2_list),
            'culture_medium_temp_value2_max_date': extra_qs[
                culture_medium_temp_value2_list.index(max(culture_medium_temp_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'culture_medium_temp_value2_min': min(culture_medium_temp_value2_list),
            'culture_medium_temp_value2_min_date': extra_qs[
                culture_medium_temp_value2_list.index(min(culture_medium_temp_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'culture_medium_temp_value2_mean': mean(culture_medium_temp_value2_list),

            'culture_medium_temp_value3_max': max(culture_medium_temp_value3_list),
            'culture_medium_temp_value3_max_date': extra_qs[
                culture_medium_temp_value3_list.index(max(culture_medium_temp_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'culture_medium_temp_value3_min': min(culture_medium_temp_value3_list),
            'culture_medium_temp_value3_min_date': extra_qs[
                culture_medium_temp_value3_list.index(min(culture_medium_temp_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'culture_medium_temp_value3_mean': mean(culture_medium_temp_value3_list),

            'nutrient_solution_ec_value1_max': max(nutrient_solution_ec_value1_list),
            'nutrient_solution_ec_value1_max_date': extra_qs[nutrient_solution_ec_value1_list.index(max(nutrient_solution_ec_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ec_value1_min': min(nutrient_solution_ec_value1_list),
            'nutrient_solution_ec_value1_min_date': extra_qs[nutrient_solution_ec_value1_list.index(min(nutrient_solution_ec_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ec_value1_mean': mean(nutrient_solution_ec_value1_list),

            'nutrient_solution_ec_value2_max': max(nutrient_solution_ec_value2_list),
            'nutrient_solution_ec_value2_max_date': extra_qs[
                nutrient_solution_ec_value2_list.index(max(nutrient_solution_ec_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ec_value2_min': min(nutrient_solution_ec_value2_list),
            'nutrient_solution_ec_value2_min_date': extra_qs[
                nutrient_solution_ec_value2_list.index(min(nutrient_solution_ec_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ec_value2_mean': mean(nutrient_solution_ec_value2_list),

            'nutrient_solution_ec_value3_max': max(nutrient_solution_ec_value3_list),
            'nutrient_solution_ec_value3_max_date': extra_qs[
                nutrient_solution_ec_value3_list.index(max(nutrient_solution_ec_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ec_value3_min': min(nutrient_solution_ec_value3_list),
            'nutrient_solution_ec_value3_min_date': extra_qs[
                nutrient_solution_ec_value3_list.index(min(nutrient_solution_ec_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ec_value3_mean': mean(nutrient_solution_ec_value3_list),

            'nutrient_solution_ph_value1_max': max(nutrient_solution_ph_value1_list),
            'nutrient_solution_ph_value1_max_date': extra_qs[nutrient_solution_ph_value1_list.index(max(nutrient_solution_ph_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ph_value1_min': min(nutrient_solution_ph_value1_list),
            'nutrient_solution_ph_value1_min_date': extra_qs[nutrient_solution_ph_value1_list.index(min(nutrient_solution_ph_value1_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ph_value1_mean': mean(nutrient_solution_ph_value1_list),

            'nutrient_solution_ph_value2_max': max(nutrient_solution_ph_value2_list),
            'nutrient_solution_ph_value2_max_date': extra_qs[
                nutrient_solution_ph_value2_list.index(max(nutrient_solution_ph_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ph_value2_min': min(nutrient_solution_ph_value2_list),
            'nutrient_solution_ph_value2_min_date': extra_qs[
                nutrient_solution_ph_value2_list.index(min(nutrient_solution_ph_value2_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ph_value2_mean': mean(nutrient_solution_ph_value2_list),

            'nutrient_solution_ph_value3_max': max(nutrient_solution_ph_value3_list),
            'nutrient_solution_ph_value3_max_date': extra_qs[
                nutrient_solution_ph_value3_list.index(max(nutrient_solution_ph_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ph_value3_min': min(nutrient_solution_ph_value3_list),
            'nutrient_solution_ph_value3_min_date': extra_qs[
                nutrient_solution_ph_value3_list.index(min(nutrient_solution_ph_value3_list))].test_date.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'nutrient_solution_ph_value3_mean': mean(nutrient_solution_ph_value3_list),
        }
        for i in value_qs:
            serializer = SensorValueSerializer(i)
            data.append(serializer.data)
        data.append(value_max_min_mean)
        return Response(data=data, status=status.HTTP_200_OK)

class FarmNumber(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def get_object(self, request):
        obj = self.request.user
        return obj
    def get(self, request):
        user = self.get_object(request)
        response_data =[]
        farm = Farm.objects.all().filter(user=user)
        j = 1
        for i in farm:
            gcg = Gcg.objects.all().get(farm=i)
            control_group_number = ControlGroup.objects.all().filter(gcg=gcg).count()
            response_data.append({'farm{}_group_number'.format(j):control_group_number})
            j += 1
        return Response(data=response_data, status=status.HTTP_200_OK)

# Create your views here.
