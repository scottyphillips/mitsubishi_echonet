"""
mitsubishi_echonet is used to provide control to Mitsubishi (and possibly other)
HVAC WiFi controllers that use the ECHONET-LITE protocol
such as the Mitsubishi MAC-IF558 adaptor.

I originally planned for this to be a full blown ECHONET library, but at this
stage it will control the AC and thats it!

"""

import socket
import struct
# import sys
# import time
from .eojx import *
# from .epc  import *
from .esv  import *
from .functions  import buildEchonetMsg
from .classes.HomeAirConditioner import *
from .classes.EchoNetNode import *

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
            edt = EPC_CODE[rx['SEOJGC']] [rx['SEOJCC']] [rx['OPC'][0]['EPC']][1](rx['OPC'][0]['EDT'])
            # edt = EPC_CODE[rx['SEOJGC']][rx['SEOJCC']][rx['OPC'][0]['EPC']][1](rx['OPC'][0]['EDT'])
            echonet_object = eval(EPC_CODE[edt['eojgc']][edt['eojcc']]['class'])(node['server'][0], edt['eojci'])
            print('ECHONET lite node discovered at {} - {} class'.format(node['server'][0], EOJX_CLASS[edt['eojgc']][edt['eojcc']]))
            if echonet_class == EOJX_CLASS[edt['eojgc']][edt['eojcc']] or echonet_class == "":
                eoa.append(echonet_object)

    return eoa
