from django.db import models
from django.conf import settings

# Create your models here.

class Farm(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    vegetable_type = models.CharField(max_length=100)
    farm_area = models.IntegerField()
    farm_type1 = models.CharField(max_length=10) # N 농
    farm_type2 = models.CharField(max_length=10) # M 중
    farm_house_num = models.CharField(max_length=10) # L 동
# Gcg Info 모델
class Gcg(models.Model):
    STATE_TYPE = (
        ('01', 'Normal'),
        ('02', 'Register Mode'),
        ('03', 'Battery Error'),
        ('04', 'Voltage Error'),
        ('05', 'Communication Error'),
        ('ff', 'Unknown Error'),
    )
    farm = models.OneToOneField('Farm', on_delete=models.PROTECT)
    serial_num = models.CharField(max_length=8)
    sw_ver = models.CharField(max_length=2, blank=True)
    sensing_period = models.CharField(max_length=6, blank=True)
    state = models.CharField(choices=STATE_TYPE, max_length=2, blank=True)
    snode_num = models.IntegerField(default=0)
    anode_num = models.IntegerField(default=0)
# 제어그룹 모델 - 한개 Gcg당 최대 16개 지정가능
class ControlGroup(models.Model):
    gcg = models.ForeignKey('Gcg', on_delete=models.PROTECT)
    num = models.IntegerField(default=0)
    name = models.IntegerField() # N 동
    # 개폐기 옵션에 제어그룹 외래키 부여
    # 센서 인포 ( 센서 value ) 에 제어그룹 외래키 부여
# 개폐제어 정보 - 한개 제어그룹당 개폐기 그룹은 8개 / auto 그룹은 6개 존재
class ControlOpenOption(models.Model):
    MODE_TYPE = (
        ('01', '자동'),
        ('02', '수동'),
    )
    SEQUENCE_TYPE = (
        ('01', '1번 그룹부터'),
        ('02', '2번 그룹부터'),
    )
    ACTIVATE_TYPE = (
        ('01', '활성화'),
        ('02', '비활성화'),
    )
    control_group = models.OneToOneField('ControlGroup', on_delete=models.PROTECT)
    motor_num = models.IntegerField(default=0)
    # open_group_info - og_info
    og_num = models.IntegerField(default=0)
        # 개폐기 그룹에 개폐기 옵션 외래키 부여
    # open_motor_option - om_option
    om_mode = models.CharField(choices=MODE_TYPE, max_length=2, blank=True)
    om_delay_time = models.IntegerField(default=0) # 단위 : 초
    om_open_sequence = models.CharField(choices=SEQUENCE_TYPE, max_length=2, blank=True)
    om_close_sequence = models.CharField(choices=SEQUENCE_TYPE, max_length=2, blank=True)
    om_rain_mode = models.CharField(choices=ACTIVATE_TYPE, max_length=2, blank=True)
    om_rain_option = models.IntegerField(default=0) # 단위 : 분
    om_high_temp_mode = models.CharField(choices=ACTIVATE_TYPE, max_length=2, blank=True)
    om_high_temp_option = models.IntegerField(default=0) # 단위 : 섭씨
        # om_auto_group에 개폐기 옵션 외래키 부여
# open_control 그룹으로 한개 option에 최대 8개의 그룹등록가능
class ControlOpenGroup(models.Model):
    ACTIVATE_TYPE = (
        ('01', '활성화'),
        ('02', '비활성화'),
    )
    control_group = models.ForeignKey('ControlGroup', on_delete=models.PROTECT)
    og_name = models.IntegerField() # 개폐기 그룹번호
    og_custom_name = models.CharField(max_length=50)
    og_mode = models.CharField(choices=ACTIVATE_TYPE, max_length=2, blank=True)
    og_tot = models.IntegerField(default=0)
    og_ot = models.IntegerField(default=0)
    og_lm_id = models.CharField(max_length=6, blank=True)
    og_rm_id = models.CharField(max_length=6, blank=True)
# open_control 주기 그룹으로 한개 option에 최대 6개의 주기그룹 등록가능
class ControlOpenAutoGroup(models.Model):
    ACTIVATE_TYPE = (
        ('01', '활성화'),
        ('02', '비활성화'),
    )
    control_group = models.ForeignKey('ControlGroup', on_delete=models.PROTECT)
    om_name = models.IntegerField()
    om_mode = models.CharField(choices=ACTIVATE_TYPE, max_length=2)
    om_stime = models.CharField(max_length=4)
    om_etime = models.CharField(max_length=4)
    om_otemp = models.FloatField()
    om_ctemp = models.FloatField()
# normal_control_option 모델로 1개의 제어그룹에 최대 1개 등록될수있다.
class ControlNormalOption(models.Model):
    control_group = models.OneToOneField('ControlGroup', on_delete=models.PROTECT)
    # flow_motor_option - fm_option
    fm_id = models.CharField(max_length=6)
    fm_stime = models.CharField(max_length=4) # 이하 start time
    fm_etime = models.CharField(max_length=4) # 이하 end time
    fm_stemp = models.FloatField() # 이하 start temp
    fm_etemp = models.FloatField() # 이하 end temp
    fm_op_time = models.IntegerField() # 단위 : 분
    fm_bk_time = models.IntegerField() # 단위 : 분
    # ventilation_motor_option
    vm_id = models.CharField(max_length=6)
    vm_stime = models.CharField(max_length=4)  # 이하 start time
    vm_etime = models.CharField(max_length=4)  # 이하 end time
    vm_stemp = models.FloatField()  # 이하 start temp
    vm_etemp = models.FloatField()  # 이하 end temp
    vm_op_time = models.IntegerField()  # 단위 : 분
    vm_bk_time = models.IntegerField()  # 단위 : 분
    # ETC_actuator_option
    ea_id = models.CharField(max_length=6)
    ea_stime = models.CharField(max_length=4)  # 이하 start time
    ea_etime = models.CharField(max_length=4)  # 이하 end time
    ea_stemp = models.FloatField()  # 이하 start temp
    ea_etemp = models.FloatField()  # 이하 end temp
    ea_op_time = models.IntegerField()  # 단위 : 분
    ea_bk_time = models.IntegerField()  # 단위 : 분
class SensorInfoOrValue(models.Model):
    control_group = models.ForeignKey('ControlGroup', on_delete=models.PROTECT)
    # temp_id
    temp_id1 = models.CharField(max_length=6)
    temp_id2 = models.CharField(max_length=6)
    temp_id3 = models.CharField(max_length=6)
    # temp_value
    temp_value1 = models.FloatField()
    temp_value2 = models.FloatField()
    temp_value3 = models.FloatField()
    # humd_id
    humd_id1 = models.CharField(max_length=6)
    humd_id2 = models.CharField(max_length=6)
    humd_id3 = models.CharField(max_length=6)
    # humd_value
    humd_value1 = models.FloatField()
    humd_value2 = models.FloatField()
    humd_value3 = models.FloatField()
    # co2_id
    co2_id1 = models.CharField(max_length=6)
    co2_id2 = models.CharField(max_length=6)
    co2_id3 = models.CharField(max_length=6)
    # co2_value
    co2_value1 = models.FloatField()
    co2_value2 = models.FloatField()
    co2_value3 = models.FloatField()
    # soil_temp_id
    soil_temp_id1 = models.CharField(max_length=6)
    soil_temp_id2 = models.CharField(max_length=6)
    soil_temp_id3 = models.CharField(max_length=6)
    # soil_temp_value
    soil_temp_value1 = models.FloatField()
    soil_temp_value2 = models.FloatField()
    soil_temp_value3 = models.FloatField()
    # soil_humd_id
    soil_humd_id1 = models.CharField(max_length=6)
    soil_humd_id2 = models.CharField(max_length=6)
    soil_humd_id3 = models.CharField(max_length=6)
    # soil_humd_value
    soil_humd_value1 = models.FloatField()
    soil_humd_value2 = models.FloatField()
    soil_humd_value3 = models.FloatField()
    # soil_ec_id
    soil_ec_id1 = models.CharField(max_length=6)
    soil_ec_id2 = models.CharField(max_length=6)
    soil_ec_id3 = models.CharField(max_length=6)
    # soil_ec_value
    soil_ec_value1 = models.FloatField()
    soil_ec_value2 = models.FloatField()
    soil_ec_value3 = models.FloatField()
    # culture_medium_temp_id
    culture_medium_temp_id1 = models.CharField(max_length=6)
    culture_medium_temp_id2 = models.CharField(max_length=6)
    cultrue_medium_temp_id3 = models.CharField(max_length=6)
    # culture_medium_temp_value
    culture_medium_temp_value1 = models.FloatField()
    culture_medium_temp_value2 = models.FloatField()
    culture_medium_temp_value3 = models.FloatField()
    # nutrient_solution_ec_id
    nutrient_solution_ec_id1 = models.CharField(max_length=6)
    nutrient_solution_ec_id2 = models.CharField(max_length=6)
    nutrient_solution_ec_id3 = models.CharField(max_length=6)
    # nutrient_solution_ec_value
    nutrient_solution_ec_value1 = models.FloatField()
    nutrient_solution_ec_value2 = models.FloatField()
    nutrient_solution_ec_value3 = models.FloatField()
    # nutrient_solution_ph_id
    nutrient_solution_ph_id1 = models.CharField(max_length=6)
    nutrient_solution_ph_id2 = models.CharField(max_length=6)
    nutrient_solution_ph_id3 = models.CharField(max_length=6)
    # nutrient_solution_ph_value
    nutrient_solution_ph_value1 = models.FloatField()
    nutrient_solution_ph_value2 = models.FloatField()
    nutrient_solution_ph_value3 = models.FloatField()
# 외부기상 info - Gcg에서 외래키 받아옴
class WeatherInfo(models.Model):
    gcg = models.ForeignKey('Gcg', on_delete=models.PROTECT)
    rain_value = models.FloatField()
    temp_value = models.FloatField()
    humd_value = models.FloatField()
    wind_dir_value = models.FloatField()
    wind_spd_value = models.FloatField()
# Sms passcode model
class SMSPassCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    passcode = models.CharField(max_length=10)