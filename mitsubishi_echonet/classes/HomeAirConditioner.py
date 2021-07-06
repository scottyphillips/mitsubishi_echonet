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
        self.setTemperature = None
        self.roomTemperature = None
        self.outdoorTemperature = None
        self.mode = False
        # self.fan_speed = None
        self.JSON = {}

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
                      0xB0] # mode
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
                    print(data['rx_edt'])
                elif data['rx_epc'] == 0xB0: #mode
                    returned_json_data.update(_30B0(data['rx_edt']))

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
            self.setTemperature = temperature
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
        if self.setMessage(0xB0, MODES[mode]):
            self.mode = mode
            return True
        else:
            return False
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
        if self.setMessage(0xA0, FAN_SPEED[fan_speed]):
            return True
        else:
            return False

    """
    GetOutdoorTemperature get the temperature that has been set in the HVAC

    return: A string representing the configured temperature.
    """
    def getOutdoorTemperature(self):
        self.outdoorTemperature = self.getMessage(0xBE)['outdoor_temperature']
        return self.outdoorTemperature


    """
    getRoomTemperature get the HVAV's room temperature.

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
        self.outdoorTemperature = self.getMessage(0xBE)['outdoor_temperature']
        return self.outdoorTemperature

    """
    setSwingMode sets the automatic swing mode function

    params swing_mode: A string representing automatic swing mode
                       e.g: 'not-used', 'vert', 'horiz', 'vert-horiz'
    """
    def setSwingMode(self, swing_mode):
        if self.setMessage(0xA3, SWING_MODE[swing_mode]):
            self.swing_mode = swing_mode
            return True
        else:
            return False

    """
    getSwingMode gets the swing mode that has been set in the HVAC

    return: A string representing the configured swing mode.
    """
    def getSwingMode(self):
        self.swing_mode = self.getMessage(0xA3)['swing_mode']
        return self.swing_mode


    """
    setAutoDirection sets the automatic direction mode function

    params auto_direction: A string representing automatic direction mode
                           e.g: 'auto', 'non-auto', 'auto-horiz', 'auto-vert'
    """
    def setAutoDirection (self, auto_direction):
        if self.setMessage(0xA1, AUTO_DIRECTION[auto_direction]):
            self.auto_direction = auto_direction
            return True
        else:
            return False

    """
    getAutoDirection get the direction mode that has been set in the HVAC

    return: A string representing the configured temperature.
    """
    def getAutoDirection(self):
        self.auto_direction = self.getMessage(0xA1)['auto_direction']
        return self.auto_direction


    """
    setAirflowVert sets the vertical vane setting

    params airflow_vert: A string representing vertical airflow setting
                         e.g: 'upper', 'upper-central', 'central',
                         'lower-central', 'lower'
    """
    def setAirflowVert (self, airflow_vert):
        if self.setMessage(0xA4, AIRFLOW_VERT[airflow_vert]):
            self.airflow_vert = airflow_vert
            return True
        else:
            return False

    """
    getAirflowVert get the vertical vane setting that has been set in the HVAC

    return: A string representing vertical airflow setting
    """
    def getAirflowVert(self):
        self.airflow_vert  = self.getMessage(0xA4)['airflow_vert']
        return self.airflow_vert

    """
    setAirflowHoriz sets the horizontal vane setting

    params airflow_horiz: A string representing horizontal airflow setting
                         e.g: 'left', 'lc', 'center', 'rc', 'right'
    """
    def setAirflowHoriz (self, airflow_horiz):
        if self.setMessage(0xA5, AIRFLOW_HORIZ[airflow_horiz]):
            self.airflow_horiz = airflow_horiz
            return True
        else:
            return False

    """
    getAirflowHoriz get the horizontal vane setting that has been set in the HVAC

    return: A string representing vertical airflow setting e.g: 'left', 'lc', 'center', 'rc', 'right'
    """
    def getAirflowHoriz(self):
        self.airflow_horiz  = self.getMessage(0xA5)['airflow_horiz']
        return self.airflow_horiz
