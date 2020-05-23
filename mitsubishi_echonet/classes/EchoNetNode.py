from ..eojx import *
from ..epc  import *
from ..esv  import *
from ..functions import *
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
