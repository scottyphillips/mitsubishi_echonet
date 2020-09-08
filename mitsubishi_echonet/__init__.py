"""
mitsubishi_echonet is used to provide control to Mitsubishi (and possibly other)
HVAC WiFi controllers that use the ECHONET-LITE protocol
such as the Mitsubishi MAC-IF558 adaptor.

I originally planned for this to be a full blown ECHONET library, but at this
stage it will control the AC and thats it!

"""

import socket
import struct
import sys
import time
from .eojx import *
from .epc  import *
from .esv  import *
from .functions  import Function as F

ENL_PORT = 3610
ENL_MULTICAST_ADDRESS = "224.0.23.0"


"""
buildEchonetMsg is used to build an ECHONET-LITE control message in the form
of a byte string

param data: a dict representing the control message.
return: an int representing the control message.
"""
def buildEchonetMsg(data):
   try:
      # EHD is fixed to 0x1081 because I am lazy.
      message = 0x1081

      # validate TID (set a default value if none provided)
      # TODO - TID message overlap.
      if 'TID' not in data:
         data['TID'] = 0x01
      elif data['TID'] > 0xFFFF:
         raise ValueError('Transaction ID is larger then 2 bytes.')
      message = (message << 16) + data['TID']

      # append SEOJ
      message = (message << 24) + 0x05FF01

      # validate DEOJ
      if data['DEOJGC'] in EOJX_GROUP:
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
          # ESV code is a string
          message = (message << 8) + data['ESV']
      else:
          raise ValueError('Value not in ESV code table')

      # validate OPC
      message = (message << 8) + len(data['OPC'])

      # You can have multiple OPC per transaction.
      for values in data['OPC']:
        # validate EPC
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


"""
decodeEchonetMsg is used to build an ECHONET-LITE control message in the form
of a byte string

param bytes: A string representing the hexadecimal control message in ECHONET LITE
return: a dict representing the deconstructed ECHONET packet
"""
def decodeEchonetMsg(byte):
  data = {}
  try:
      data['EHD1'] = byte[0]
      if data['EHD1'] not in EHD1:
          raise ValueError('EHD1 Header invalid')
      data['EHD2'] = byte[1]
      if data['EHD2'] not in EHD2:
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

"""
sendMessage is used for ECHONET Unicast and Multicast transcations
message is assumed a correctly formatted ECHONET string
sendMessage will receive multiple messages if multicast is used "eg 224.0.23.0"

param message: an int representing the ECHONET message
param ip_address: a string representing the IPv4 address e.g "1.2.3.4"

return: an array representing the received response from the ECHONET message
"""
def sendMessage(message, ip_address):
    data =[]
    transaction_group = (ip_address, ENL_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_open = True
    while True:
        try:
            sock.bind(('',ENL_PORT))
            break
        except OSError:
            # Wait for socket to be open:
            time.sleep(0.5)

    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    sock.settimeout(0.5)

    # Set the time-to-live for messages to 1 so they do not
    # go past the local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        sent = sock.sendto(bytearray.fromhex(message), transaction_group)
        # Look for responses from all recipients
        while True:
            try:
                payload, server = sock.recvfrom(1024)
            except socket.timeout:
                break
            else:
                # Received a packet.
                data.append({'server':server,'payload':payload})
    finally:
        sock.close()
    return data

"""
discover is used to identify ECHONET nodes. Original plan was for this library
to fully support a multitude of ECHONET devices.

return: an array of discovered ECHONET node objects.
"""
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
    # Build ECHONET discover messafge.
    message = buildEchonetMsg(tx_payload)

    # Send message to multicast group and receive data
    data = sendMessage(message, ENL_MULTICAST_ADDRESS);
    # Decipher received message for each node discovered:

    for node in data:
        rx = decodeEchonetMsg(node['payload'])
        if (tx_payload['DEOJGC'] == rx['SEOJGC'] and
        rx['TID'] == tx_payload['TID'] and
        rx['OPC'][0]['EPC'] == 0xd6):
            # Action EDT payload by calling applicable function using lookup table
            edt = EPC_CODE[rx['SEOJGC']][rx['SEOJCC']][rx['OPC'][0]['EPC']][1](rx['OPC'][0]['EDT'])
            e = eval(EPC_CODE[edt['eojgc']][edt['eojcc']]['class'])(node['server'][0], edt['eojci'])
            print('ECHONET lite node discovered at {} - {} class'.format(node['server'][0], EOJX_CLASS[edt['eojgc']][edt['eojcc']]))
            if echonet_class != "":
                if echonet_class == EOJX_CLASS[edt['eojgc']][edt['eojcc']] or echonet_class == "":
                    eoa.append(e)
            else:
                eoa.append(e)

    return eoa

"""
opCode is used to return details from a node using the lookup table

return: an dict containing the properties of the node.
"""
def getOpCode(ip_address, deojgc, deojcc, deojci, opc, tid=0x01):
        tx_payload = {
            'TID' : tid, # Transaction ID 1
            'DEOJGC': deojgc,
            'DEOJCC': deojcc,
            'DEOJIC': deojci,
            'ESV' : GET,
            'OPC' : opc
        }
        # Build ECHONET discover message.
        message = buildEchonetMsg(tx_payload)
        rx_data = sendMessage(message, ip_address)
        return_data = {}
        if len(rx_data) > 0:
            rx = decodeEchonetMsg(rx_data[0]['payload'])
            # Action EDT payload by calling applicable function using lookup table
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
    # setProperties = getOpCode(ip_address, deojgc, deojcc, deojci, [{'EPC':0x9E}])
    # print(property_map)
    for property in property_map:
        propertyMaps[property] = {}
        for value in property_map[property]:
            if value in EPC_CODE[0x01][0x30]['functions']:
                propertyMaps[property][EPC_CODE[0x01][0x30]['functions'][value][0]] = value
            elif value in EPC_SUPER:
                propertyMaps[property][EPC_SUPER[value][0]] = value
            # else:
                 #print("code not found: " + hex(value) )
    return propertyMaps

"""
Superclass for Echonet node objects.
"""
class EchoNetNode:

    """
    Construct a new 'EchoNet' object.

    :param instance: Instance ID
    :param netif: IP address of node
    """
    def __init__(self, instance = 0x1, netif="", polling = 10 ):
        self.netif = netif
        self.last_transaction_id = 0x1
        self.eojgc = None
        self.eojcc = None
        self.instance = instance
        self.available_functions = None
        self.status = False
        self.propertyMaps = {}

    """
    getMessage is used to fire ECHONET request messages to get Node information
    Assumes one EPC is sent per message.

    :param tx_epc: EPC byte code for the request.
    :return: the deconstructed payload for the response
    """
    def getMessage(self, epc, pdc = 0x00):
        self.last_transaction_id += 1
        opc = [{'EPC': epc, 'PDC': pdc}]
        edt = getOpCode(self.netif, self.eojgc, self.eojcc, self.instance, opc, self.last_transaction_id )
        return edt


    """
    setMessage is used to fire ECHONET request messages to set Node information
    Assumes one OPC is sent per message.

    :param tx_epc: EPC byte code for the request.
    :param tx_edt: EDT data relevant to the request.
    :return: the deconstructed payload for the response
    """
    def setMessage(self, tx_epc, tx_edt):
        self.last_transaction_id += 1
        # fix for rollover of transaction ID which was causing home assistant to crash
        if self.last_transaction_id == 0xFFFF:
            self.last_transaction_id == 0
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
        ## some index issue here sometimes
        try:
           rx = decodeEchonetMsg(data[0]['payload'])
        # if no data is returned ignore the IndexError and return false
        except IndexError:
           return False
        rx_epc = rx['OPC'][0]['EPC']
        rx_pdc = rx['OPC'][0]['PDC']
        if rx_epc == tx_epc and rx_pdc == 0x00:
            return True
        else:
            return False

    """
    getOperationalStatus returns the ON/OFF state of the node

    :return: status as a string.
    """
    def getOperationalStatus(self): # EPC 0x80
        return self.getMessage(0x80)


    """
    setOperationalStatus sets the ON/OFF state of the node

    :param status: True if On, False if Off.
    """
    def setOperationalStatus(self, status): # EPC 0x80
        return self.setMessage(0x80, 0x30 if status else 0x31)

    """
    On sets the node to ON.

    """
    def on (self): # EPC 0x80
        return self.setMessage(0x80, 0x30)

    """
    Off sets the node to OFF.

    """
    def off (self): # EPC 0x80
        return self.setMessage(0x80, 0x31)

    def fetchSetProperties (self): # EPC 0x80
        if 'setProperties' in self.propertyMaps:
            return self.propertyMaps['setProperties']
        else:
            return {}

    def fetchGetProperties (self): # EPC 0x80
        if 'getProperties' in self.propertyMaps:
            return self.propertyMaps['getProperties']
        else:
            return {}

"""Class for Home AirConditioner Objects"""
class HomeAirConditioner(EchoNetNode):

    """
    Construct a new 'HomeAirConditioner' object.
    In theory this would work for any ECHNONET enabled domestic AC.

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
        self.swing_mode = None
        self.auto_direction = None
        self.airflow_vert = None
        self.airflow_horiz = None
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
                      0xB0, # mode
                      0xA3, # swing mode
                      0xBE] # outdoor temp
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
            self.swing_mode = self.JSON['swing_mode']
            self.outdoorTemperature = self.JSON['outdoor_temperature']
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
    getFanSpeed gets the current fan speed (e.g Low, Medium, High etc)

    return: A string representing the fan speed
    """
    def getFanSpeed(self):
        self.fan_speed = self.getMessage(0xA0)['fan_speed']
        return self.fan_speed


    """
    setFanSpeed set the desired fan speed (e.g Low, Medium, High etc)

    param fan_speed: A string representing the fan speed
    """
    def setFanSpeed(self, fan_speed):
        if self.setMessage(0xA0, FAN_SPEED[fan_speed]):
            self.fanspeed = fan_speed
            return True
        else:
            return False

    """
    getOutdoorTemperature get the temperature that has been set in the HVAC

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
		
