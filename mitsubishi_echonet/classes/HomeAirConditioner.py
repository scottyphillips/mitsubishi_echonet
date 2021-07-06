#import socket
#import struct
#import sys
#import time
#from ..eojx import *
# from ..epc  import *
# from ..esv  import *
# from ..functions  import Function as F
from .EchoNetNode import EchoNetNode
from ..functions import *

# Check status of Air Conditioner
def _3080(edt):
    ops_value = int.from_bytes(edt, 'big')
    return {'status': ('On' if ops_value == 0x30 else 'Off')}

# Check status of Configured Temperature
def _30B3(edt):
    return {'set_temperature': int.from_bytes(edt, 'big')}

# Check status of Room Temperature
def _30BB(edt):
    return {'room_temperature': int.from_bytes(edt, 'big')}

# Check status of Outdoor Temperature
def _30BE(edt):
    return {'outdoor_temperature': int.from_bytes(edt, 'big')}

# Check status of Fan speed
def _30A0(edt):
    op_mode = int.from_bytes(edt, 'big')
    values = {
       0x41: 'auto',
       0x31: 'minimum',
       0x32: 'low',
       0x33: 'medium-low',
       0x34: 'medium',
       0x35: 'medium-high',
       0x36: 'high',
       0x37: 'very-high',
       0x38: 'max'
    }
    return {'fan_speed': values.get(op_mode, "Invalid setting")}


def _30AA(edt):
    op_mode = int.from_bytes(edt, 'big')
    # print(hex(op_mode))
    values = {
      0x40: 'Normal operation',
      0x41: 'Defrosting',
      0x42: 'Preheating',
      0x43: 'Heat removal'
      }
    # return({'special':hex(op_mode)})
    return {'special_setting': values.get(op_mode, "Invalid setting")}

# Operation mode
def _30B0(edt):
    op_mode = int.from_bytes(edt, 'big')
    values = {
       0x41: 'auto',
       0x42: 'cool',
       0x43: 'heat',
       0x44: 'dry',
       0x45: 'fan_only',
       0x40: 'other'
    }
    return {'mode': values.get(op_mode, "Invalid setting" )}

# Automatic control of air flow direction setting
def _30A1(edt):
    op_mode = int.from_bytes(edt, 'big')
    values = {
       0x41: 'auto',
       0x42: 'non-auto',
       0x43: 'auto-vert',
       0x44: 'auto-horiz'
    }
    return {'auto_direction': values.get(op_mode, "Invalid setting")}

# Automatic swing of air flow direction setting
def _30A3(edt):
    op_mode = int.from_bytes(edt, 'big')
    values = {
       0x31: 'not-used',
       0x41: 'vert',
       0x42: 'horiz',
       0x43: 'vert-horiz'
    }
    return {'swing_mode': values.get(op_mode, "Invalid setting")}

# Air flow direction (vertical) setting
def _30A4(edt):
    op_mode = int.from_bytes(edt, 'big')
    values = {
      0x41: 'upper',
      0x44: 'upper-central',
      0x43: 'central',
      0x45: 'lower-central',
      0x42: 'lower'
      }
    # return({'special':hex(op_mode)})
    return {'airflow_vert': values.get(op_mode, "Invalid setting")}

# Air flow direction (horiziontal) setting
def _30A5(edt):
    # complies with version 2.01 Release a (page 3-88)
    op_mode = int.from_bytes(edt, 'big')
    values = {
      0x41: 'rc-right',
      0x42: 'left-lc',
      0x43: 'lc-center-rc',
      0x44: 'left-lc-rc-right',
      0x51: 'right',
      0x52: 'rc',
      0x54: 'center',
      0x55: 'center-right',
      0x56: 'center-rc',
      0x57: 'center-rc-right',
      0x58: 'lc',
      0x59: 'lc-right',
      0x5A: 'lc-rc',
      0x60: 'left',
      0x61: 'left-right',
      0x62: 'left-rc',
      0x63: 'left-rc-right',
      0x64: 'left-center',
      0x65: 'left-center-right',
      0x66: 'left-center-rc',
      0x67: 'left-center-rc-right',
      0x69: 'left-lc-right',
      0x6A: 'left-lc-rc'
      }
    # return({'special':hex(op_mode)})
    return {'airflow_horiz': values.get(op_mode, "Invalid setting")}

"""Class for Home AirConditioner Objects"""
class HomeAirConditioner(EchoNetNode):

    """
    Construct a new 'HomeAirConditioner' object.
    In theory this would work for any ECHONET enabled domestic AC.

    :param instance: Instance ID
    :param netif: IP address of node
    """
    def __init__(self, netif, instance = 0x1):
        EchoNetNode.__init__(self, instance, netif)
        self.eojgc = 0x01
        self.eojcc = 0x30
        # self.available_functions = EPC_CODE[self.eojgc][self.eojcc]['functions']
        # self.propertyMaps = getAllPropertyMaps(self.netif, self.eojgc, self.eojcc , self.instance)

    """
    update is used as a quick and dirty way of producing a dict useful for API polling etc
    This exists primarily for home assistant!

    return: A string with the following attributes:
    {'status': '###', 'set_temperature': ##, 'fan_speed': '###', 'room_temperature': ##, 'mode': '###'}

    """
    def update(self):
        # at this stage we only care about a subset of gettable attributes that are relevant
        # down the track i might try to pull all of them..
        attributes = [0x80, # Op status
                      0xB3, # Set temperature
                      0xA0, # fan speed
                      0xBB, # room temperature
                      0xB0, # mode
                      0xBE] # outdoor temperature
                      #0x8A] # manufactorers code
        opc = []
        returned_json_data = {}
        self.last_transaction_id += 1
        for value in attributes:
        #  if value in self.propertyMaps['getProperties'].values():
            opc.append({'EPC': value})
        raw_data = getOpCode(self.netif, self.eojgc, self.eojcc, self.instance, opc, self.last_transaction_id )
        if raw_data is not False:
             for data in raw_data:
                if data['rx_epc'] == 0x80: #Op status
                    print(data['rx_edt'])
                elif data['rx_epc'] == 0xB3: #Set Temperature
                    returned_json_data.update(_30B3(data['rx_edt']))
                elif data['rx_epc'] == 0xA0: #fan speed
                    returned_json_data.update(_30A0(data['rx_edt']))
                elif data['rx_epc'] == 0xBB: #room temperature
                    returned_json_data.update(_30BB(data['rx_edt']))
                elif data['rx_epc'] == 0xB0: #mode
                    returned_json_data.update(_30B0(data['rx_edt']))
                elif data['rx_epc'] == 0xBE: #mode
                    returned_json_data.update(_30BE(data['rx_edt']))

        return returned_json_data

    """
    GetOperationaTemperature get the temperature that has been set in the HVAC

    return: A string representing the configured temperature.
    """
    def getOperationalTemperature(self):
        raw_data = self.getMessage(0xB3)[0]
        if raw_data['rx_epc'] == 0xB3:
            return _30B3(raw_data['rx_edt'])


    """
    setOperationalTemperature get the temperature that has been set in the HVAC

    param temperature: A string representing the desired temperature.
    """
    def setOperationalTemperature(self, temperature):
        if self.setMessage(0xB3, int(temperature)):
            return True
        else:
            return False

    """
    GetMode returns the current configured mode (e.g Heating, Cooling, Fan etc)

    return: A string representing the configured mode.
    """
    def getMode(self):
        raw_data = self.getMessage(0xB0)[0]
        if raw_data['rx_epc'] == 0xB0:
            return _30B0(raw_data['rx_edt'])

    """
    setMode set the desired mode (e.g Heating, Cooling, Fan etc)

    param mode: A string representing the desired mode.
    """
    def setMode(self, mode):
        return self.setMessage(0xB0, MODES[mode])

    """
    GetFanSpeed gets the current fan speed (e.g Low, Medium, High etc)
    Refer EPC code 0xA0: ('Air flow rate setting')

    return: A string representing the fan speed
    """
    def getFanSpeed(self):
        #self.fan_speed = self.getMessage(0xA0)
        raw_data = self.getMessage(0xA0)[0]
        if raw_data['rx_epc'] == 0xA0:
            return _30A0(raw_data['rx_edt'])
        # return self.fan_speed


    """
    setFanSpeed set the desired fan speed (e.g Low, Medium, High etc)

    param fans_speed: A string representing the fan speed
    """
    def setFanSpeed(self, fan_speed):
        return self.setMessage(0xA0, FAN_SPEED[fan_speed])

    """
    getRoomTemperature get the HVAC's room temperature.

    return: A string representing the room temperature.
    """
    def getRoomTemperature(self):
        raw_data = self.getMessage(0xBB)[0]
        if raw_data['rx_epc'] == 0xBB:
            return _30BB(raw_data['rx_edt'])

    """
    getOutdoorTemperature get the outdoor temperature that has been set in the HVAC

    return: A string representing the configured outdoor temperature.
    """
    def getOutdoorTemperature(self):
        raw_data= self.getMessage(0xBE)[0]
        if raw_data['rx_epc'] == 0xBE:
           return _30BE(raw_data['rx_edt'])

    """
    setSwingMode sets the automatic swing mode function

    params swing_mode: A string representing automatic swing mode
                       e.g: 'not-used', 'vert', 'horiz', 'vert-horiz'
    """
    def setSwingMode(self, swing_mode):
        return self.setMessage(0xA3, SWING_MODE[swing_mode])

    """
    getSwingMode gets the swing mode that has been set in the HVAC

    return: A string representing the configured swing mode.
    """
    def getSwingMode(self):
        raw_data = self.getMessage(0xA3)[0]
        if raw_data['rx_epc'] == 0xA3:
            return _30A3(raw_data['rx_edt'])


    """
    setAutoDirection sets the automatic direction mode function

    params auto_direction: A string representing automatic direction mode
                           e.g: 'auto', 'non-auto', 'auto-horiz', 'auto-vert'
    """
    def setAutoDirection (self, auto_direction):
        return self.setMessage(0xA1, AUTO_DIRECTION[auto_direction])

    """
    getAutoDirection get the direction mode that has been set in the HVAC

    return: A string representing the configured temperature.
    """
    def getAutoDirection(self):
        raw_data = self.getMessage(0xA1)[0]
        if raw_data['rx_epc'] == 0xA1:
            return _30A1(raw_data['rx_edt'])


    """
    setAirflowVert sets the vertical vane setting

    params airflow_vert: A string representing vertical airflow setting
                         e.g: 'upper', 'upper-central', 'central',
                         'lower-central', 'lower'
    """
    def setAirflowVert (self, airflow_vert):
        return self.setMessage(0xA4, AIRFLOW_VERT[airflow_vert])

    """
    getAirflowVert get the vertical vane setting that has been set in the HVAC

    return: A string representing vertical airflow setting
    """
    def getAirflowVert(self):
        raw_data = self.getMessage(0xA4)[0]
        if raw_data['rx_epc'] == 0xA4:
            return _30A4(raw_data['rx_edt'])

    """
    setAirflowHoriz sets the horizontal vane setting

    params airflow_horiz: A string representing horizontal airflow setting
                         e.g: 'left', 'lc', 'center', 'rc', 'right'
    """
    def setAirflowHoriz (self, airflow_horiz):
        return self.setMessage(0xA5, AIRFLOW_HORIZ[airflow_horiz])

    """
    getAirflowHoriz get the horizontal vane setting that has been set in the HVAC

    return: A string representing vertical airflow setting e.g: 'left', 'lc', 'center', 'rc', 'right'
    """
    def getAirflowHoriz(self):
        raw_data = self.getMessage(0xA5)[0]
        if raw_data['rx_epc'] == 0xA5:
            return _30A5(raw_data['rx_edt'])
