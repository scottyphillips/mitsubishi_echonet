#!/usr/bin/env python3
import mitsubishi_echonet as mit
import time

# Discover HVAC Echonet objects
# while aircons == False:
instances = mit.discover("192.168.1.6")
print(instances)
aircon = mit.HomeAirConditioner("192.168.1.6")
#for aircon in aircons:
print("Airconditioner {} available Get properties:".format(aircon.netif))
   #print(aircon.netif)
print(aircon.fetchGetProperties())
#
#   print("Airconditioner {} available Set
#properties:".format(aircon.netif))
#   print(aircon.fetchSetProperties())

#   aircon.on()
#   aircon.setMode('heat')

#   print("Getting current operational parameters")
#   print(aircon.update())
   # aircon.setFanSpeed('medium-low')

#   print("Getting outdoor temperature")
print(aircon.getOutdoorTemperature())
