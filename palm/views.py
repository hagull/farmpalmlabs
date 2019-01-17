from django.shortcuts import render, get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics, mixins, viewsets, status, views
from django.contrib.auth import get_user_model
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from statistics import mean
from palm.ap_processing import *
from .models import *
from .serializers import *

# DB에 센싱데이터 저장시에 display date처리 ( 분이 5의 배수형태 )
def convert_to_time(input_date):
    minute = input_date.minute
    minute = (minute//5)*5
    output_date = input_date.replace(minute=minute, second=0, microsecond=0)
    return output_date


# user 정보 조회를 위한 viewset ( modelviewset )
# 유저정보 조회 get / 특정 유저정보 조회 get ( 인자로 pk값 )
# 유저정보 추가 post ( user model의 field를 post의 바디에 지정)
# 유저정보 수정 put/patch ( pk값 필요 )
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # 일반적으로 접근하면 전체 user정보 / 토큰인증을 통한 접근을하면 토큰에 해당하는 유저정보조회
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(username=self.request.user)
        return qs


# farm 정보 조회 및 수정을 위한 viewset(modelviewset)
# 유저정보와 마찬가지의 format을 지닌다.
class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # farm 등록시 수행할 작업의 정의 ( 하지만 실제로 농장등록은 다른 view를 통해 진행 )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs

# 비밀번호 찾기시에 sms를 통한 인증번호 + 유저아이디 + 유저핸드폰번호를 통해 token을 발행
# post요청 바디 데이터 = (username, phonem passcode)
class FindPasswordTokenView(views.APIView):
    permission_classes = [AllowAny]

    def get_object(self, request):
        data = request.data
        user = get_object_or_404(User, username=data['username'], phone=data['phone'])
        return user
    def get(self, request):
        return Response(data="None")
    # post요청으로 위에 정의한 바디데이터들이 일치할경우 user에 해당하는 토큰값을 반환한다.
    def post(self, request):
        data = request.data
        user = self.get_object(request)
        # sms 인증시 usernaem과 phone를 통해 생성된 인증번호와 전송받은 인증번호를 비교
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

# 비밀번호 변경시의 APIView
# put요청으로 기존비밀번호와 새로운비밀번호를 바디에 실어서 보냈을때 처리
class SetPasswordView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    # put 요청으로 기존비밀번호와 새로운 비밀번호를 받게되었을때 기존비밀번호가 일치하였을때 새로운 비밀번호로 재설정
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

# 비밀번호 찾기 이후의 비밀번호 재설정을 위한 APIView
# put 요청으로 이전 class FindPasswordTokenView를 통해 발급받은 토큰을 헤더에 실은 후 바디에 새로운 패스워드를 실어서 요청
class SetPasswordAtFindView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    # put 요청으로 헤더에 토큰, 바디데이터에 새로운 패스워드
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response({'status':'set password'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 비밀번호 찾기시 토큰을 발급받기전 SMS 인증을 위한 APIView
# 아직 미구현 상태 https://www.coolsms.co.kr/download/60711 참고
# 이 작업이 끝나면 생성된 passcode는 지우는 것을 권장
class SMSPasscodeView(views.APIView):
    permission_classes = [AllowAny]

    def get_object(self, request):
        data = request.data
        user = get_object_or_404(User, username=data['username'], phone=data['phone'])
        return user
    # get 혹은 post요청시 전달받은 유저 아이디와 핸드폰번호로 user 객체를 가져오고 이 user 객체의 외래키를 가지는 SMSPasscode 모델에 새로운 데이터 생성
    def get(self, request):
        return Response(data="None")

    def post(self, request):
        # 이 공간에서 Passcode를 생성 -> DB저장 -> SMS 송신이 이루어진다.
        pass

# 농장 등록시의 apiview
class RegisterFarmView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self, request):
        user = self.request.user
        return user

    def get(self, request):
        return Response(data="only post request" ,status = status.HTTP_400_BAD_REQUEST)
    # post 요청으로 farm model field값, gcg_id, extra_info( '1.(왼쪽개폐기아이디).(오른쪽개폐기아이디).1측천창/1.(왼쪽개폐기아이디).(오른쪽개폐기아이디).1측측창'의 데이터 포멧을 가지는)를 실어서 요청
    # 이는 사전객체의 리스트로 대체가능 ( app에서 전송시에 편한 방식을 채택 )
    def post(self, request):
        user = self.get_object(request)
        data = request.data # farn  모델 정보, gcg_id, extra_info
        extra_info = data.pop('extra_info')
        gcg_id = data.pop('gcg_id')
        farm = Farm.objects.create(user=user, **data)
        gcg = Gcg.objects.create(farm=farm, serial_num=gcg_id)
        # extra_info 데이터 처리 / N동에는 M개의 컨트롤 그룹이 있고 각 개폐기 그룹의 custom name은 다음과 같다는 형식으로 지정
        extra_info_list = extra_info.split('/')
        for i in extra_info_list:
            step1 = i.split('.')
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

# 날씨데이터 조회시의 APIView, 이때 농장을 기준으로 하기때문에 요청시에 gcg_id 필요 ( serial_num )
class WeatherValueView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, request):
        data = request.data
        gcg_id = data['gcg_id']
        gcg = Gcg.objects.all().get(serial_num=gcg_id)
        weather_value = WeatherInfo.objects.filter(gcg=gcg).order_by('-test_date').first()
        return weather_value
    # post 요청시 바디 데이터로 gcg_id 를 받아 처리한다.
    def post(self, request):
        weather_value = self.get_object(request)
        serializer = WeatherValueSerializer(weather_value)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 센싱데이터 조회시
# 센싱데이터 조회는 동을 기준으로 한다. 즉 gcg_id 와 control_group_name을 바디데이터로 전달받는다.
class SensorValueView(views.APIView):
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

    # post요청은 이 1시간 단위로 쪼개진 24개의 센싱데이터 출력과 24시간동안 측정된 데이터의 최대값 최소값 평균값에 대한 처리를 한다.
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


# 각 농장마다 control group 수를 표시해주는 API view
# 만든 이유는 각 농장에 대해 몇개의 동이 있는지 표시하기 위한 페이지를 위해
# farm model viewset에선 pk값으로 지정되기 때문에 gcg_id를 통해 반환
class FarmNumberView(views.APIView):
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


# protocol 처리를 위한 view
class ProtocolView(views.APIView):
    permission_classes = [AllowAny]
    # get인자를 통해 protocol을 처리함 - 현재 센싱데이터 처리만 정의
    def get(self, request, protocol):
        protocol = protocol
        ap3_2 = AP3_2(protocol=protocol)
        list_data = None
        if ap3_2.command_type =='06':
            ap3_2 = AP3_2_SERVICE(protocol=protocol)
            if ap3_2.payload_type =='01':
                gcg_id = ap3_2.gcg
                gcg = Gcg.objects.get(serial_num = gcg_id)
                list_data = ap3_2.message_receive()
                for i in list_data:
                    control_group_name = i.pop('control_group_name')
                    control_group = ControlGroup.objects.get(gcg=gcg, name=control_group_name)
                    sensor_value = SensorInfoOrValue.objects.create(control_group=control_group, **i)
                    sensor_value.display_date = convert_to_time(sensor_value.display_date)
                    if sensor_value.display_date.minute == 0:
                        sensor_value.display_data = True
                    sensor_value.save()
            else:
                pass
        else:
            pass
        return Response(data=list_data, status=status.HTTP_200_OK)
# Create your views here.
