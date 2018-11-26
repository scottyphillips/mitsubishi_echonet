from mitsubishi_echonet  import epc, esv, mitsubishi as mit
from threading import Thread
import random, time

class EchoNetNode:
    """Class for Echonet Objects"""
    def __init__(self, message, netif="", polling = 10 ):
        Thread.__init__(self)
        self.netif = netif
        self.last_transaction_id = 0
        self.self_eojgc = None
        self.self_eojcc = None
        self.instance = None
        self.available_functions = None
        self.status = False

    def GetMessage(self, tx_epc):
        self.last_transaction_id += 1
        tx_payload = {
        'TID' : self.last_transaction_id,
        'DEOJGC': self.self_eojgc ,
        'DEOJCC': self.self_eojcc ,
        'DEOJIC': self.instance,
        'ESV' : esv.GET,
        'OPC' : [{'EPC': tx_epc, 'PDC': 0x00}]
        }
        message = mit.BuildEchonetMsg(tx_payload)

        data = mit.SendMessage(message, self.netif);
        rx = mit.DecodeEchonetMsg(data[0]['payload'])
        rx_edt = rx['OPC'][0]['EDT']
        rx_epc = rx['OPC'][0]['EPC']
        value = epc.CODE[self.self_eojgc][self.self_eojcc]['functions'][rx_epc][1](rx_edt)
        return value

    def SetMessage(self, tx_epc, tx_edt):
        self.last_transaction_id += 1
        tx_payload = {
        'TID' : self.last_transaction_id,
        'DEOJGC': self.self_eojgc ,
        'DEOJCC': self.self_eojcc ,
        'DEOJIC': self.instance,
        'ESV' : esv.SETC,
        'OPC' : [{'EPC': tx_epc, 'PDC': 0x01, 'EDT': tx_edt}]
        }
        message = mit.BuildEchonetMsg(tx_payload)
        data = mit.SendMessage(message, self.netif);
        rx = mit.DecodeEchonetMsg(data[0]['payload'])
        rx_epc = rx['OPC'][0]['EPC']
        rx_pdc = rx['OPC'][0]['PDC']
        if rx_epc == tx_epc and rx_pdc == 0x00:
        # value = epc.CODE[self.self_eojgc][self.self_eojcc]['functions'][rx_epc][1](rx_edt)
            return True
        else:
            return False

    def GetOperationalStatus(self): # EPC 0x80
        print("Checking Operational Status..")
        self.status = self.GetMessage(0x80)['status']
        if self.status == 'On':
            print("The node is switched ON")
        else:
            print("The node is switched OFF")

    def SetOperationalStatus(self, status): # EPC 0x80
        print("Setting Operational Status..")
        self.SetMessage(0x80, 0x30 if status else 0x31)
        # if self.status == True:
        #    print("The node is switched ON")
        # else:
        #    print("The node is switched OFF")

    def On (self): # EPC 0x80
        print("Switching on..")
        self.SetMessage(0x80, 0x30)

    def Off (self): # EPC 0x80
        print("Switching off..")
        self.SetMessage(0x80, 0x31)

class HomeAirConditioner(EchoNetNode):
    """Class for Home AirConditioner Objects"""
    def __init__(self, message, netif):
        EchoNetNode.__init__(self, message, netif)
        self.self_eojgc = 0x01
        self.self_eojcc = 0x30
        self.instance = message['instance']
        self.last_transaction_id = message['TID']
        self.available_functions = epc.CODE[self.self_eojgc][self.self_eojcc]['functions']
        self.setTemperature = None
        self.roomTemperature = None
        self.mode = False
        self.fan_speed = None
        self.JSON = {}

    def Update(self):
        self.last_transaction_id += 1
        tx_payload = {
        'TID' : self.last_transaction_id,
        'DEOJGC': self.self_eojgc ,
        'DEOJCC': self.self_eojcc ,
        'DEOJIC': self.instance,
        'ESV' : esv.GET,
        'OPC' : [{'EPC':0x80},{'EPC': 0xB3},{'EPC': 0xA0},{'EPC': 0xBB},{'EPC': 0xB0}]
        }

        message = mit.BuildEchonetMsg(tx_payload)
        data = mit.SendMessage(message, self.netif);
        try:
            rx = mit.DecodeEchonetMsg(data[0]['payload'])
        except IndexError as error:
            print('No Data Received')
            return self.JSON
        for data in rx['OPC']:
            rx_edt = data['EDT']
            rx_epc = data['EPC']
            value = epc.CODE[self.self_eojgc][self.self_eojcc]['functions'][rx_epc][1](rx_edt)
            self.JSON.update(value)
            self.setTemperature = self.JSON['set_temperature']
            self.mode = self.JSON['mode']
            self.fan_speed = self.JSON['fan_speed']
            self.roomTemperature = self.JSON['room_temperature']
            self.status = self.JSON['status']

        print(self.JSON)
        return self.JSON


    def GetOperationlTemperature(self):
        self.setTemperature = self.GetMessage(0xB3)['temperature']
        # print("Current configured unit temperature is " + str(self.setTemperature) + " Degrees")

    def SetOperationlTemperature(self, temperature):
        print("Setting the configured temperature to " + str(temperature))
        if self.SetMessage(0xB3, temperature):
            print("Temperature set sucessfully")
        self.GetOperationlTemperature()

    def GetMode(self):
        # print("Getting the current operating mode")
        self.mode = self.GetMessage(0xB0)['mode']
        print("Current configured mode is " + str(self.mode))

    def SetMode(self, mode):
        print("Set the current operating mode")
        if self.SetMessage(0xB0, esv.MODES[mode]):
            print("Mode set sucessfully")
        self.GetMode()

    def GetFanSpeed(self):
        # print("Getting the current fan speed")
        self.fan_speed = self.GetMessage(0xA0)['fan_speed']
        print("Fan speed is " + str(self.fan_speed))

    def SetFanSpeed(self, fan_speed):
        print("Set the current fan speed")
        if self.SetMessage(0xA0, esv.FAN_SPEED[fan_speed]):
            print("Fan Speed set sucessfully")
        self.GetFanSpeed()
