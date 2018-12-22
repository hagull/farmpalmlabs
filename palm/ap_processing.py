# palm/ap_processing.py
# ap 처리를 위한 모듈을 저장하는 공간
import struct
import datetime
# AP3_1 Processing
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

    pass