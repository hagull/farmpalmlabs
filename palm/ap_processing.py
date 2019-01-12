# palm/ap_processing.py
# ap 처리를 위한 모듈을 저장하는 공간
import struct
import datetime
# AP3_1 Processing
def str_to_float(str_value):
    step1 = [int(str_value[6:8], 16), int(str_value[4:6], 16), int(str_value[2:4], 16), int(str_value[:2], 16)]
    step2 = bytes(step1)
    step3 = struct.unpack('>f', step2)
    step4 = step3[0]
    step5 = round(step4, 3)
    return step5
class AP3_1:
    def __init__(self, command_type = 0, version = 1, frame_type = 0, security = 0, sequence_number = 0):
        self.frame_header = '0x'
        self.version = hex(version)[2:].rjust(2, '0')
        self.frame_type = hex(frame_type)[2:].rjust(2, '0')
        self.security = hex(security)[2:].rjust(2, '0')
        self.sequence = hex(sequence_number)[2:].rjust(4, '0')
        self.command_type = hex(command_type)[2:].rjust(2, '0')
        self.frame_header = self.frame_header + self.version + self.frame_type + self.security + self.sequence + self.command_type
# command type = 0x01 : Gcg info requests and settings
class AP3_1_GCG(AP3_1):
    def __init__(self, command_type = 1, version = 1, frame_type = 0, security = 0, sequence_number = 0):
        super().__init__(command_type, version, frame_type, security, sequence_number, )
    # payload type = 0x01 : Gcg info requests
    def gcg_info(self, value1,  payload_type = 1):
        payload_type = hex(payload_type)[2:].rjust(2, '0')
        value1 = hex(value1)[2:].rjust(2, '0')
        protocol = self.frame_header + payload_type + value1
        return protocol
    # payload type = 0x02 : Gcg set the info requests
    def gcg_set(self, value1, value2, payload_type=2):
        payload_type = hex(payload_type)[2:].rjust(2, '0')
        value1 = hex(value1)[2:].rjust(2, '0')
        if type(value2) == int:
            value2 = hex(value2)[2:]
        # value1 0x01 : Gcg set the id
        if value1 == '01':
            value2 = value2.rjust(8, '0')
        # value1 0x02 : Gcg set the sw_ver
        elif value1 == '02':
            value2 = value2.rjust(2, '0')
        # value1 0x03 : Gcg set the service_server_ip
        elif value1 == '03':
            value2 = value2.rjust(8, '0')
        # value1 0x04 : Gcg set the Sensing period
        elif value1 == '04':
            value2 = value2.isoformat(timespec='seconds')
            value2 = value2[:2] + value2[3:5] + value2[6:8]
        # value1 undefined : return the error_code
        else:
            error_code = 'undefined value1 at command type 0x01 & payload type 0x02'
            return error_code
        protocol = self.frame_header + payload_type + value1 + value2
        return protocol
class AP3_1_NODE(AP3_1):
    def __init__(self, command_type=2, version=1, frame_type=0, security=0, sequence_number=0):
        super().__init__(command_type, version, frame_type, security, sequence_number)
    # payload type = 0x01 : Snode info requests
    def snode_info(self, value1, value2, value3, payload_type = 1):
        payload_type = hex(payload_type)[2:].rjust(2, '0')
        value1 = hex(value1)[2:].rjust(2, '0')
        value2 = hex(value2)[2:].rjust(2, '0')
        protocol = self.frame_header + payload_type + value1 + value2 + value3
        return protocol
    # payload type = 0x02 : Snode set the info requests
    def snode_set(self, value1, value2, value3 = 0, payload_type = 2):
        payload_type = hex(payload_type)[2:].rjust(2, '0')
        value1 = hex(value1)[2:].rjust(2, '0')
        value2 = value2.rjust(4, '0')
        if ((value1 == '01') | (value1 == '02')):
            protocol = self.frame_header + payload_type + value1 + value2
        else:
            protocol = self.frame_header + payload_type + value1 + value2 + value3
        return protocol
    # payload type = 0x03 : Anode info requests
    def anode_info(self, value1, value2, value3, payload_type = 3):
        payload_type = hex(payload_type)[2:].rjust(2, '0')
        value1 = hex(value1)[2:].rjust(2, '0')
        value2 = hex(value2)[2:].rjust(2, '0')
        protocol = self.frame_header + payload_type + value1 + value2 + value3
        return protocol
    # payload type = 0x04 : Anode set the info requests
    def anode_set(self, value1, value2, value3='0', value4=0, value5='0', payload_type = 4):
        payload_type = hex(payload_type)[2:].rjust(2, '0')
        value1 = hex(value1)[2:].rjust(2, '0')
        value2 = value2.rjust(4, '0')
        if value1 == '03':
            value3 = value3.rjust(4, '0')
            value4 = hex(value4)[2:].rjust(2, '0')
            value5 = value5.rjust(6, '0')
            protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5
        else:
            protocol = self.frame_header + payload_type + value1 + value2
        return protocol
# command type = 0x03 : Control group requests
class AP3_1_CONTROL(AP3_1):
    def __init__(self, command_type=2, version=1, frame_type=0, security=0, sequence_number=0):
        super().__init__(command_type, version, frame_type, security, sequence_number)
    # payload type = 0x01 : control group info requests
    def group_info(self, value1, value2 = 0, value3 = 0, value4 = 0, payload_type = 1):
        payload_type = hex(payload_type)[2:].rjust(2, '0')
        value1 = hex(value1)[2:].rjust(2, '0')
        if value1 == '02':
            value2 = hex(value2)[2:].rjust(2, '0')
            value3 = hex(value3)[2:].rjust(2, '0')
            if ((value3 == 'FF') | (value3 =='ff')):
                protocol = self.frame_header + payload_type + value1 + value2 + value3
            else:
                value4 = hex(value4)[2:].rjust(2, '0')
                protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4
        else:
            protocol = self.frame_header + payload_type + value1
        return protocol
    # payload type = 0x02 : control group set the info requests
    def group_set(self, value1, value2, value3, value4, value5, value6=None, value7=None, value8=None, payload_type = 2):
        payload_type = hex(payload_type)[2:].rjust(2, '0')
        value1 = hex(value1)[2:].rjust(2, '0')
        protocol = ''
        if value1=='01':
            value2 = hex(value2)[2:].rjust(2, '0')
            if value2=='01':
                value3 = hex(value3)[2:].rjust(2, '0')
                if value3 =='01':
                    value4 = hex(value4)[2:].rjust(2, '0')
                    value5 = hex(value5)[2:].rjust(2, '0')
                    if value5 == '01':
                        value6 = value6.rjust(2, '0')
                        protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5 + value6
                    elif value5 == '02':
                        value6 = value6.rjust(196, '0')
                        protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5 + value6
                    elif value5 == '03':
                        value6 = value6.rjust(54, '0')
                        protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5 + value6
                elif ((value3 =='02') | (value3 =='03') | (value3 =='04')):
                    value4 = hex(value4)[2:].rjust(2, '0')
                    value5 = value5.rjsut(28, '0')
                    protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5
            elif value2=='02':
                value3 = hex(value3).rjust(2, '0')
                value4 = hex(value4).rjust(2, '0')
                if value3 == '01':
                    value5 = value5.rjust(128, '0')
                    protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5
                elif (value3 =='02') | (value3 == '03'):
                    value5 = value5.rjust(96, '0')
                    protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5
                elif value3 == '04':
                    value5 = value5.rjust(192, '0')
                    protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5
                elif value3 == '05':
                    value5 = value5.rjust(162, '0')
                    protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5
            elif value2=='03':
                value3 = hex(value3)[2:].rjust(2, '0')
                if value3 == '01':
                    value4 = hex(value4)[2:].rjust(2, '0')
                    value5 = hex(value5)[2:].rjust(2, '0')
                    if value5 == '01':
                        value6 = hex(value6)[2:].rjust(2, '0')
                        protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5 + value6
                    elif value5 == '02':
                        value6 = hex(value6)[2:].rjust(2, '0')
                        if value6 =='01':
                            value7 = hex(value7)[2:].rjust(2, '0')
                            protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5 + value6 + value7
                        elif value6 == '02':
                            value7 = hex(value7)[2:].rjust(2, '0')
                            value8 = value8.rjust(24, '0') # 임시 ID 의 byte범위에 따라 달라짐
                            protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5 + value6 + value7 + value8
                elif (value3 == '02') | (value3 == '03') | (value3 == '04'):
                    value4 = hex(value4)[2:].rjust(2, '0')
                    value5 = hex(value5)[2:].rjust(2, '0')
                    value6 = hex(value6)[2:].rjust(2, '0')
                    protocol = self.frame_header + payload_type + value1 + value2 + value3 + value4 + value5 + value6
        elif value1 == '02':
            pass
        elif value1 == '03':
            pass
        else:
            pass
        return protocol
# command type = 0x04 : Log list requests
class AP3_1_LOG(AP3_1):
    def __init__(self, command_type=2, version=1, frame_type=0, security=0, sequence_number=0):
        super().__init__(command_type, version, frame_type, security, sequence_number)
    # payload type = 0x01 : Log record requests at 24 hour
    def log_today(self):
        pass
    # payload type = 0x02 : Log record requests at all
    def log_all(self):
        pass
class AP3_2:
    def __init__(self, protocol):
        self.protocol = protocol[2:]
        self.version = self.protocol[:2] # 1byte
        self.frame_type = self.protocol[2:4] # 1byte
        self.security = self.protocol[4:6] # 1byte
        self.sequence = self.protocol[6:10] # 2byte
        self.gcg = self.protocol[10:18] # 4byte
        self.command_type = self.protocol[18:20] # 1byte
        self.payload_type = self.protocol[20:22] # 1byte
class AP3_2_SERVICE(AP3_2):
    def __init__(self, protocol):
        super().__init__(protocol)
        if self.payload_type == '01':
            self.value1 = self.protocol[22:24] # 1byte
            self.value2 = self.protocol[24:26] # 1byte
            self.value3 = self.protocol[26:] # (235*value2)byte
    def message_receive(self):
        # value1 = 0x01 : 센서 값 전송
        if self.value1 == '01':
            control_group_num = int(self.value2, 16)
            split_protocol = []
            value3 = self.value3
            temp_data = value3[:470]
            rest_data = value3[470:]
            for i in range(control_group_num):
                data = {}
                data['control_group_name'] = int(temp_data[:2], 16) # 1byte
                data['temp_num'] = int(temp_data[2:4], 16)
                data['temp_id1'] = temp_data[4:10]
                data['temp_id2'] = temp_data[10:16]
                data['temp_id3'] = temp_data[16:22]

                data['humd_num'] = int(temp_data[22:24], 16)
                data['humd_id1'] = temp_data[24:30]
                data['humd_id2'] = temp_data[30:36]
                data['humd_id3'] = temp_data[36:42]

                data['co2_num'] = int(temp_data[42:44], 16)
                data['co2_id1'] = temp_data[44:50]
                data['co2_id2'] = temp_data[50:56]
                data['co2_id3'] = temp_data[56:62]

                data['soil_temp_num'] = int(temp_data[62:64], 16)
                data['soil_temp_id1'] = temp_data[64:70]
                data['soil_temp_id2'] = temp_data[70:76]
                data['soil_temp_id3'] = temp_data[76:82]

                data['soil_humd_num'] = int(temp_data[82:84], 16)
                data['soil_humd_id1'] = temp_data[84:90]
                data['soil_humd_id2'] = temp_data[90:96]
                data['soil_humd_id3'] = temp_data[96:102]

                data['soil_ec_num'] = int(temp_data[102:104], 16)
                data['soil_ec_id1'] = temp_data[104:110]
                data['soil_ec_id2'] = temp_data[110:116]
                data['soil_ec_id3'] = temp_data[116:122]

                data['culture_medium_temp_num'] = int(temp_data[122:124], 16)
                data['culture_medium_temp_id1'] = temp_data[124:130]
                data['culture_medium_temp_id2'] = temp_data[130:136]
                data['culture_medium_temp_id3'] = temp_data[136:142]

                data['nutrient_solution_ec_num'] = int(temp_data[142:144], 16)
                data['nutrient_solution_ec_id1'] = temp_data[144:150]
                data['nutrient_solution_ec_id2'] = temp_data[150:156]
                data['nutrient_solution_ec_id3'] = temp_data[156:162]

                data['nutrient_solution_ph_num'] = int(temp_data[162:164], 16)
                data['nutrient_solution_ph_id1'] = temp_data[164:170]
                data['nutrient_solution_ph_id2'] = temp_data[170:176]
                data['nutrient_solution_ph_id3'] = temp_data[176:182]

                data['temp_value1'] = str_to_float(temp_data[182:190])
                data['temp_value2'] = str_to_float(temp_data[190:198])
                data['temp_value3'] = str_to_float(temp_data[198:206])
                data['temp_mean'] = str_to_float(temp_data[206:214])

                data['humd_value1'] = str_to_float(temp_data[214:222])
                data['humd_value2'] = str_to_float(temp_data[222:230])
                data['humd_value3'] = str_to_float(temp_data[230:238])
                data['humd_mean'] = str_to_float(temp_data[238:246])

                data['co2_value1'] = str_to_float(temp_data[246:254])
                data['co2_value2'] = str_to_float(temp_data[254:262])
                data['co2_value3'] = str_to_float(temp_data[262:270])
                data['co2_mean'] = str_to_float(temp_data[270:278])

                data['soil_temp_value1'] = str_to_float(temp_data[278:286])
                data['soil_temp_value2'] = str_to_float(temp_data[286:294])
                data['soil_temp_value3'] = str_to_float(temp_data[294:302])
                data['soil_temp_mean'] = str_to_float(temp_data[302:310])

                data['soil_humd_value1'] = str_to_float(temp_data[310:318])
                data['soil_humd_value2'] = str_to_float(temp_data[318:326])
                data['soil_humd_value3'] = str_to_float(temp_data[326:334])
                data['soil_humd_mean'] = str_to_float(temp_data[334:342])

                data['soil_ec_value1'] = str_to_float(temp_data[342:350])
                data['soil_ec_value2'] = str_to_float(temp_data[350:358])
                data['soil_ec_value3'] = str_to_float(temp_data[358:366])
                data['soil_ec_mean'] = str_to_float(temp_data[366:374])

                data['culture_medium_temp_value1'] = str_to_float(temp_data[374:382])
                data['culture_medium_temp_value2'] = str_to_float(temp_data[382:390])
                data['culture_medium_temp_value3'] = str_to_float(temp_data[390:398])
                data['culture_medium_temp_mean'] = str_to_float(temp_data[398:406])

                data['nutrient_solution_ec_value1'] = str_to_float(temp_data[406:414])
                data['nutrient_solution_ec_value2'] = str_to_float(temp_data[414:422])
                data['nutrient_solution_ec_value3'] = str_to_float(temp_data[422:430])
                data['nutrient_solution_ec_mean'] = str_to_float(temp_data[430:438])

                data['nutrient_solution_ph_value1'] = str_to_float(temp_data[438:446])
                data['nutrient_solution_ph_value2'] = str_to_float(temp_data[446:454])
                data['nutrient_solution_ph_value3'] = str_to_float(temp_data[454:462])
                data['nutrient_solution_ph_mean'] = str_to_float(temp_data[462:470])
                split_protocol.append(data)
                temp_data = rest_data[:470]
                rest_data = rest_data[470:]
            return split_protocol
        else:
            pass