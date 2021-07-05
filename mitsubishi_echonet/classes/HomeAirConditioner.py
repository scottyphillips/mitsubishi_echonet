import socket
import struct
import sys
import time
from ..eojx import *
from ..epc  import *
from ..esv  import *
# from ..functions  import Function as F
from .EchoNetNode import EchoNetNode
from ..functions import *

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
        self.available_functions = EPC_CODE[self.eojgc][self.eojcc]['functions']
        self.propertyMaps = getAllPropertyMaps(self.netif, self.eojgc, self.eojcc , self.instance)
        self.setTemperature = None
        self.roomTemperature = None
        self.outdoorTemperature = None
        self.mode = False
        self.fan_speed = None
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
        self.last_transaction_id += 1
        for value in attributes:
          if value in self.propertyMaps['getProperties'].values():
             opc.append({'EPC': value})
        returned_data = getOpCode(self.netif, self.eojgc, self.eojcc, self.instance, opc, self.last_transaction_id )
        if returned_data is not False:
            self.JSON = returned_data
            self.setTemperature = self.JSON['set_temperature']
            self.mode = self.JSON['mode']
            self.fan_speed = self.JSON['fan_speed']
            self.roomTemperature = self.JSON['room_temperature']
            self.status = self.JSON['status']
        return returned_data

    """
    GetOperationaTemperature get the temperature that has been set in the HVAC

    return: A string representing the configured temperature.
    """
    def getOperationalTemperature(self):
        self.setTemperature = self.getMessage(0xB3)['set_temperature']
        return self.setTemperature


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
        self.mode = self.getMessage(0xB0)['mode']
        return self.mode

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

    return: A string representing the fan speed
    """
    def getFanSpeed(self):
        self.fan_speed = self.getMessage(0xA0)['fan_speed']
        return self.fan_speed


    """
    setFanSpeed set the desired fan speed (e.g Low, Medium, High etc)

    param fans_speed: A string representing the fan speed
    """
    def setFanSpeed(self, fan_speed):
        if self.setMessage(0xA0, FAN_SPEED[fan_speed]):
            self.fanspeed = fan_speed
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
