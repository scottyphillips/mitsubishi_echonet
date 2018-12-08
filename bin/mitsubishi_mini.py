"""
Minified version of mitsubishi.py with ECHONET API built in.

"""
GETC = 			0x60
SETC = 			0x61
GET  = 			0x62
SETGET = 		0x6E
SETRES =		0x71
GETRES =		0x72
INF =			0x73
INFC = 			0x74
INFC_RES =		0x7A
SETGET_RES =	0x7E

MODES = {
	'Automatic':		0x41,
	'Cooling':  		0x42,
	'Heating':  		0x43,
	'Dehumidification': 0x44,
	'Air circulator':	0x45,
	'Other': 			0x40
}

FAN_SPEED = {
	'Automatic':	0x41,
	'Minimum':  	0x31,
	'Low':  		0x32,
	'Medium-Low': 	0x33,
	'Medium':		0x34,
	'Medium-High': 	0x35,
	'High':			0x36,
	'Very High':    0x37,
	'Max':			0x38
}

ESV_CODES = {
	0x60: {'name': 'GetC', 'description': 'Property value write request (no response required)'},
	0x61: {'name': 'SetC', 'description': 'Property value write request (response required)'},
	0x62: {'name': 'Get', 'description': 'Property value read request'},
	0x63: {'name': 'INF_REQ', 'description': 'Property value notification request'},
	0x6E: {'name': 'SetGet', 'description': 'Property value write & read request'},
	0x71: {'name': 'Set_Res', 'description': 'Property value Property value write response'},
	0x72: {'name': 'Get_Res' , 'description': 'Property value read response'},
	0x73: {'name': 'INF' , 'description': 'Property value notification'},
	0x74: {'name': 'INFC', 'description': 'Property value notification (response required)'},
	0x7A: {'name': 'INFC_Res' , 'description': 'Property value notification response'},
	0x7E: {'name': 'SetGet_Res' , 'description': 'Property value write & read response'},
}

EOJX_CLASS = {
	0x01: {
		0x30: 'Home air conditioner'
	},
	0x0E: {
		0xF0: 'Node profile'
	}
}


EOJX_GROUP = {
	0x01: 'Air conditioner-related device group',
	0x0E: 'Profile group',
};

class Function:
    def _0EF0D6(edt):
        data = int.from_bytes(edt, 'big')
        edtnum = int((data & 0xff000000) / 0x1000000)
        eojgc = int((data & 0x00ff0000) / 0x10000)
        eojcc = int((data & 0x0000ff00) / 0x100)
        eojci = int(data & 0x000000ff)

        return {
          "eojgc": eojgc,
          "eojcc": eojcc,
          "eojci": eojci
        }
    # Check status of Air Conditioner
    def _013080(edt):
        ops_value = int.from_bytes(edt, 'big')
        return {'status': ('On' if ops_value == 0x30 else 'Off')}

    # Check status of Configured Temperature
    def _0130B3(edt):
        return {'set_temperature': int.from_bytes(edt, 'big')}

    # Check status of Room Temperature
    def _0130BB(edt):
        return {'room_temperature': int.from_bytes(edt, 'big')}

    # Check status of Fan speed
    def _0130A0(edt):
        op_mode = int.from_bytes(edt, 'big')
        values = {
           0x41: 'Automatic',
           0x31: 'Minimum',
           0x32: 'Low',
           0x33: 'Medium-Low',
           0x34: 'Medium',
           0x35: 'Medium-High',
           0x36: 'High',
           0x37: 'Very High',
           0x38: 'Max'
        }
        return {'fan_speed': values.get(op_mode, "Invalid setting")}


    def _0130AA(edt):
        op_mode = int.from_bytes(edt, 'big')
        print(hex(op_mode))
        values = {
          0x40: 'Normal operation',
          0x41: 'Defrosting',
          0x42: 'Preheating',
          0x43: 'Heat removal'
          }
        # return({'special':hex(op_mode)})
        return {'special_setting': values.get(op_mode, "Invalid setting")}

    # Operation mode
    def _0130B0(edt):
        op_mode = int.from_bytes(edt, 'big')
        values = {
           0x41: 'Automatic',
           0x42: 'Cooling',
           0x43: 'Heating',
           0x44: 'Dehumidification',
           0x45: 'Air circulator',
           0x40: 'Other'
        }
        return {'mode': values.get(op_mode, "Invalid setting" )}

    def _FF009E(edt):
        return {'setProperties': Function._FF009X(edt)}

    def _FF009F(edt):
        return {'getProperties': Function._FF009X(edt)}

    def _FF009X(edt):
        payload = []
        if len(edt) < 17:
            for i in range (1, len(edt)):
                payload.append(edt[i])
            return payload

        for i in range (1, len(edt)):
            code = i-1
            binary = '{0:08b}'.format(edt[i])[::-1]
            for j in range (0, 8):
                if binary[j] == "1":
                    EPC = (j+8) * 0x10 + code
                    payload.append(EPC)
        return payload


EPC_CODE = {
	0x01: { # Air conditioner-related device class group
		0x30: { # Home air conditioner class
			"class": 'HomeAirConditioner',
			"functions": {
				0x80: ('Operation status', Function._013080),
				0xB0: ('Operation mode setting', Function._0130B0 ),
				0xB3: ('Set temperature value', Function._0130B3),
				0xBB: ('Measured value of room temperature', Function._0130BB),
				0xA0: ('Air flow rate setting', Function._0130A0),
				0xAA: ('Special state', Function._0130AA),
			}
		},
    },
	0x0E: { # Profile class group
		0xF0: { # Node profile class
			0xD6: ('Self-node instance list S', Function._0EF0D6),
			# Super Class of the Profile class group
		}
	}
}

EPC_SUPER = {
	0x9E: ('Set property map', Function._FF009E),
	0x9F: ('Get property map', Function._FF009F)
}

import logging
import socket
import struct
import sys

from homeassistant.components.climate import (
    ClimateDevice, ATTR_TARGET_TEMP_HIGH, ATTR_TARGET_TEMP_LOW,
    SUPPORT_TARGET_TEMPERATURE, SUPPORT_TARGET_HUMIDITY,
    SUPPORT_TARGET_HUMIDITY_LOW, SUPPORT_TARGET_HUMIDITY_HIGH,
    SUPPORT_AWAY_MODE, SUPPORT_HOLD_MODE, SUPPORT_FAN_MODE,
    SUPPORT_OPERATION_MODE, SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE_HIGH, SUPPORT_TARGET_TEMPERATURE_LOW,
    SUPPORT_ON_OFF)
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT, ATTR_TEMPERATURE, CONF_HOST, CONF_IP_ADDRESS, CONF_NAME

DOMAIN = "mitsubishi"
SUPPORT_FLAGS = SUPPORT_TARGET_HUMIDITY_LOW | SUPPORT_TARGET_HUMIDITY_HIGH

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):

    """Set up the Mitsubishi ECHONET climate devices."""
    add_entities([
        MitsubishiClimate(config.get(CONF_NAME),
           HomeAirConditioner(config.get(CONF_IP_ADDRESS)),
           TEMP_CELSIUS)
    ])

ENL_PORT = 3610
ENL_MULTICAST_ADDRESS = "224.0.23.0"

def buildEchonetMsg(data):
   try:
      message = 0x1081
      if 'TID' not in data:
         data['TID'] = 0x01
      elif data['TID'] > 0xFFFF:
         raise ValueError('Transaction ID is larger then 2 bytes.')
      message = (message << 16) + data['TID']
      message = (message << 24) + 0x05FF01

      if data['DEOJGC'] in EOJX_CLASS:
          message = (message << 8) + data['DEOJGC']
      else:
          raise ValueError('Value ' + str(hex(data['DEOJGC'])) + ' not a valid SEO Group code')

      if data['DEOJCC'] in EOJX_CLASS[data['DEOJGC']]:
          message = (message << 8) + data['DEOJCC']
      else:
          raise ValueError('Value ' + str(hex(data['DEOJCC'])) + ' not a valid SEO class code')
      message = (message << 8) + data['DEOJIC']

      # validate ESV by looking up the codes.
      if data['ESV'] in ESV_CODES:
          message = (message << 8) + data['ESV']
      else:
          raise ValueError('Value not in ESV code table')

      message = (message << 8) + len(data['OPC'])
      for values in data['OPC']:
        message =  (message << 8) + values['EPC']
        if 'PDC' in values:
            message =  (message << 8) + values['PDC']
        # if PDC has a value then concat EDT to message
            if values['PDC'] > 0:
                message =  (message << 8 * values['PDC']) + values['EDT']
        else:
            message =  (message << 8) + 0x00
      return format(int(message), 'x')
# some sloppy error handling here.
   except ValueError as error:
        # print('Caught this error: ' + repr(error))
        quit()


def decodeEchonetMsg(byte):
  data = {}
  try:
      data['EHD1'] = byte[0]
      if data['EHD1'] != 0x10:
          raise ValueError('EHD1 Header invalid')
      data['EHD2'] = byte[1]
      if data['EHD2'] != 0x81:
          raise ValueError('EHD2 Header invalid')
      data['TID'] = int.from_bytes(byte[2:4], byteorder='big')

      # Decode SEOJ
      data['SEOJGC'] = byte[4]
      data['SEOJCC'] = byte[5]
      data['SEOJIC'] = byte[6]
      # Decode DEOJ
      data['DEOJGC'] =  byte[7]
      data['DEOJCC'] =  byte[8]
      data['DEOJIC'] =  byte[9]

      # Decode Service property
      data['ESV'] =  byte[10]

      i = 0
      epc_pointer = 12
      data['OPC'] = []
      # decode multiple processing properties (OPC)
      while i <  (byte[11]):
          OPC = {}
          pdc_pointer = epc_pointer + 1
          edt_pointer = pdc_pointer + 1
          end_pointer = edt_pointer
          OPC['EPC'] = byte[epc_pointer]
          OPC['PDC'] =  byte[pdc_pointer]
          pdc_len = byte[pdc_pointer]
          end_pointer += pdc_len
          OPC['EDT'] = byte[edt_pointer:end_pointer]
          epc_pointer = end_pointer
          i += 1
          data['OPC'].append(OPC)

  except ValueError as error:
        print('Caught this error: ' + repr(error))
        quit()
  return data

def sendMessage(message, ip_address):
    data =[]
    transaction_group = (ip_address, ENL_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('',ENL_PORT))
    sock.settimeout(0.5)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        sent = sock.sendto(bytearray.fromhex(message), transaction_group)
        while True:
            try:
                payload, server = sock.recvfrom(1024)
            except socket.timeout:
                break
            else:
                data.append({'server':server,'payload':payload})
    finally:
        sock.close()
    return data

def discover(echonet_class = ""):
    eoa = []; # array containing echonet objects
    tx_payload = {
        'TID' : 0x01, # Transaction ID 1
        'DEOJGC': 0x0E,
        'DEOJCC': 0xF0,
        'DEOJIC': 0x00,
        'ESV' : 0x62,
        'OPC' : [{'EPC': 0xD6}]
    }

    message = buildEchonetMsg(tx_payload)
    data = sendMessage(message, ENL_MULTICAST_ADDRESS);

    for node in data:
        rx = decodeEchonetMsg(node['payload'])
        if (tx_payload['DEOJGC'] == rx['SEOJGC'] and
        rx['TID'] == tx_payload['TID'] and
        rx['OPC'][0]['EPC'] == 0xd6):
            edt = EPC_CODE[rx['SEOJGC']][rx['SEOJCC']][rx['OPC'][0]['EPC']][1](rx['OPC'][0]['EDT'])
            e = eval(EPC_CODE[edt['eojgc']][edt['eojcc']]['class'])(node['server'][0], edt['eojci'])
            if echonet_class == EOJX_CLASS[edt['eojgc']][edt['eojcc']] or echonet_class == "":
                eoa.append(e)
    return eoa

def getOpCode(ip_address, deojgc, deojcc, deojci, opc, tid=0x01):
        tx_payload = {
            'TID' : tid, # Transaction ID 1
            'DEOJGC': deojgc,
            'DEOJCC': deojcc,
            'DEOJIC': deojci,
            'ESV' : GET,
            'OPC' : opc
        }
        message = buildEchonetMsg(tx_payload)
        tx_data = sendMessage(message, ip_address);
        rx = decodeEchonetMsg(tx_data[0]['payload'])
        return_data = {}
        for value in rx['OPC']:
            rx_edt = value['EDT']
            rx_epc = value['EPC']
            if rx_epc in EPC_CODE[deojgc][deojcc]['functions']:
                edt = EPC_CODE[deojgc][deojcc]['functions'][rx_epc][1](rx_edt)
            else:
                edt = EPC_SUPER[rx_epc][1](rx_edt)
            return_data.update(edt)
        return return_data

def getAllPropertyMaps(ip_address, deojgc, deojcc, deojci):
    propertyMaps = {}
    property_map = getOpCode(ip_address, deojgc, deojcc, deojci, [{'EPC':0x9F},{'EPC':0x9E}])
    for property in property_map:
        propertyMaps[property] = {}
        for value in property_map[property]:
            if value in EPC_CODE[0x01][0x30]['functions']:
                propertyMaps[property][EPC_CODE[0x01][0x30]['functions'][value][0]] = value
            elif value in EPC_SUPER:
                propertyMaps[property][EPC_SUPER[value][0]] = value
    return propertyMaps

class EchoNetNode:
    def __init__(self, instance = 0x1, netif="", polling = 10):
        self.netif = netif
        self.last_transaction_id = 0x1
        self.eojgc = None
        self.eojcc = None
        self.instance = instance
        self.available_functions = None
        self.status = False
        self.propertyMaps = {}

    def getMessage(self, epc, pdc = 0x00):
        self.last_transaction_id += 1
        opc = [{'EPC': epc, 'PDC': pdc}]
        edt = getOpCode(self.netif, self.eojgc, self.eojcc, self.instance, opc, self.last_transaction_id )
        return edt

    def setMessage(self, tx_epc, tx_edt):
        self.last_transaction_id += 1
        tx_payload = {
        'TID' : self.last_transaction_id,
        'DEOJGC': self.eojgc ,
        'DEOJCC': self.eojcc ,
        'DEOJIC': self.instance,
        'ESV' : SETC,
        'OPC' : [{'EPC': tx_epc, 'PDC': 0x01, 'EDT': tx_edt}]
        }
        message = buildEchonetMsg(tx_payload)
        data = sendMessage(message, self.netif);
        rx = decodeEchonetMsg(data[0]['payload'])

        rx_epc = rx['OPC'][0]['EPC']
        rx_pdc = rx['OPC'][0]['PDC']
        if rx_epc == tx_epc and rx_pdc == 0x00:
            return True
        else:
            return False

    def getOperationalStatus(self): # EPC 0x80
        return self.getMessage(0x80)

    def setOperationalStatus(self, status): # EPC 0x80
        return self.setMessage(0x80, 0x30 if status else 0x31)

    def on (self): # EPC 0x80
        return self.setMessage(0x80, 0x30)

    def off (self): # EPC 0x80
        return self.setMessage(0x80, 0x31)

    def fetchSetProperties (self): # EPC 0x80
        return self.propertyMaps['setProperties']

    def fetchGetProperties (self): # EPC 0x80
        return self.propertyMaps['getProperties']

"""Class for Home AirConditioner Objects"""
class HomeAirConditioner(EchoNetNode):
    def __init__(self, netif, instance = 0x1):
        EchoNetNode.__init__(self, instance, netif)
        self.eojgc = 0x01
        self.eojcc = 0x30
        self.available_functions = EPC_CODE[self.eojgc][self.eojcc]['functions']
        self.propertyMaps = getAllPropertyMaps(self.netif, self.eojgc, self.eojcc , self.instance)
        self.setTemperature = None
        self.roomTemperature = None
        self.mode = False
        self.fan_speed = None
        self.JSON = {}

    def update(self):
        attributes = [0x80, # Op status
                      0xB3, # Set temperature
                      0xA0, # fan speed
                      0xBB, # room temperature
                      0xB0] # mode
        opc = []
        self.last_transaction_id += 1
        for value in attributes:
          if value in self.propertyMaps['getProperties'].values():
             opc.append({'EPC': value})
        self.JSON = getOpCode(self.netif, self.eojgc, self.eojcc, self.instance, opc, self.last_transaction_id )
        self.setTemperature = self.JSON['set_temperature']
        self.mode = self.JSON['mode']
        self.fan_speed = self.JSON['fan_speed']
        self.roomTemperature = self.JSON['room_temperature']
        self.status = self.JSON['status']
        return self.JSON

    def getOperationalTemperature(self):
        self.setTemperature = self.getMessage(0xB3)['set_temperature']
        return self.setTemperature

    def setOperationalTemperature(self, temperature):
        if self.setMessage(0xB3, int(temperature)):
            self.setTemperature = temperature
            return True
        else:
            return False

    def getMode(self):
        self.mode = self.getMessage(0xB0)['mode']
        return self.mode

    def setMode(self, mode):
        if self.setMessage(0xB0, MODES[mode]):
            self.mode = mode
            return True
        else:
            return False

    def getFanSpeed(self):
        self.fan_speed = self.getMessage(0xA0)['fan_speed']
        return self.fan_speed

    def setFanSpeed(self, fan_speed):
        if self.setMessage(0xA0, FAN_SPEED[fan_speed]):
            self.fanspeed = fan_speed
            return True
        else:
            return False


class MitsubishiClimate(ClimateDevice):
    """Representation of a Mitsubishi ECHONET climate device."""
    def __init__(self, name, echonet_hvac, unit_of_measurement):

        """Initialize the climate device."""
        self._name = name
        self._api = echonet_hvac #new line
        _LOGGER.debug("ECHONET lite HVAC component added on %s", self._api.netif)
        _LOGGER.debug("Available get attributes are %s", self._api.fetchGetProperties())
        available_properties = self._api.fetchGetProperties()

        self._unit_of_measurement = unit_of_measurement
        self._support_flags = SUPPORT_FLAGS

        # if is_on is not None:
        self._support_flags = self._support_flags | SUPPORT_ON_OFF

        if 'Operation mode setting' in available_properties:
           self._support_flags = self._support_flags | SUPPORT_OPERATION_MODE

        if 'Set temperature value' in available_properties:
           self._support_flags = self._support_flags | SUPPORT_TARGET_TEMPERATURE

        if 'Air flow rate setting' in available_properties:
           self._support_flags = self._support_flags | SUPPORT_FAN_MODE

        data = self._api.update()

        # Current and Target temperature
        self._target_temperature = data['set_temperature']
        self._current_temperature = data['room_temperature']

        # Mode and fan speed
        self._current_fan_mode = data['fan_speed']
        self._current_operation = data['mode']

        #self._fan_list = ['On Low', 'On High', 'Auto Low', 'Auto High', 'Off']
        self._fan_list = ['Low', 'Medium-High']
        self._operation_list = ['Heating', 'Cooling', 'Air circulator', 'Dehumidification', 'Automatic']
        self._swing_list = ['Auto', '1', '2', '3', 'Off']

        self._on = True if data['status'] is 'On' else False


    def update(self):
        """Get the latest state from the HVAC."""
        data = self._api.update()
        self._target_temperature = data['set_temperature']
        self._current_temperature = data['room_temperature']
        self._current_fan_mode = data['fan_speed']
        self._current_operation =  data['mode']
        self._on = True if data['status'] is 'On' else False

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def current_operation(self):
        """Return current operation ie. heat, cool, idle."""
        return self._current_operation

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return self._operation_list

    @property
    def is_on(self):
        """Return true if the device is on."""
        return self._on

    @property
    def current_fan_mode(self):
        """Return the fan setting."""
        return self._current_fan_mode

    @property
    def fan_list(self):
        """Return the list of available fan modes."""
        return self._fan_list

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._api.setOperationalTemperature(kwargs.get(ATTR_TEMPERATURE))
            self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
        if kwargs.get(ATTR_TARGET_TEMP_HIGH) is not None and \
           kwargs.get(ATTR_TARGET_TEMP_LOW) is not None:
            self._target_temperature_high = kwargs.get(ATTR_TARGET_TEMP_HIGH)
            self._target_temperature_low = kwargs.get(ATTR_TARGET_TEMP_LOW)
        self.schedule_update_ha_state()

    def set_fan_mode(self, fan_mode):
        """Set new target temperature."""
        self._api.setFanSpeed(fan_mode)
        self._current_fan_mode = fan_mode
        self.schedule_update_ha_state()

    def set_operation_mode(self, operation_mode):
        """Set new operation mode."""
        self._api.setMode(operation_mode)
        self._current_operation = operation_mode
        self.schedule_update_ha_state()

    def turn_on(self):
        """Turn on."""
        self._api.on()
        self._on = True
        self.schedule_update_ha_state()

    def turn_off(self):
        """Turn off."""
        self._api.off()
        self._on = False
        self.schedule_update_ha_state()
