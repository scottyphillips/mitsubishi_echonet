#!/usr/bin/env python3
import mitsubishi_echonet as mit
import time

aircons = False
# Discover HVAC Echonet objects
while aircons == False:
    print("Discovering Anything..")
    aircons = mit.discover()

for aircon in aircons:
   print("ECHONET {} available Get properties:".format(aircon.netif))
   #print(aircon.netif)
   print(aircon.fetchGetProperties())

   print("ECHONET {} available Set properties:".format(aircon.netif))
   print(aircon.fetchSetProperties())

   # aircon.on()
   # aircon.setMode('dry')

   # print("Getting current operational parameters")
   # print(aircon.update())
   # aircon.setFanSpeed('medium-low')

   # print("Getting outdoor temperature")
   # print(aircon.getOutdoorTemperature())
