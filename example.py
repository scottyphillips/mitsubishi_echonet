#!/usr/bin/env python3
import mitsubishi_echonet as mit
import time

aircons = False
# Discover HVAC Echonet objects
while aircons == False:
    print("Discovering Anything..")
    echonet_objects = mit.discover()

for node in echonet_objects:
   print("ECHONET node {} available Get properties:".format(aircon.netif))
   #print(aircon.netif)
   print(node.fetchGetProperties())

   print("ECHONET node {} available Set properties:".format(aircon.netif))
   print(node.fetchSetProperties())

   # aircon.on()
   # aircon.setMode('dry')

   # print("Getting current operational parameters")
   # print(aircon.update())
   # aircon.setFanSpeed('medium-low')

   # print("Getting outdoor temperature")
   # print(aircon.getOutdoorTemperature())
