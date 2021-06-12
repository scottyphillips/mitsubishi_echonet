#!/usr/bin/env python3
import mitsubishi_echonet as mit
import time

echonet_objects = False
# Discover HVAC Echonet objects
while echonet_objects == False:
    print("Discovering Anything..")
    echonet_objects = mit.discover()

for node in echonet_objects:
   print("ECHONET node {} available Get properties:".format(node.netif))
   #print(aircon.netif)
   print(node.fetchGetProperties())

   print("ECHONET node {} available Set properties:".format(node.netif))
   print(node.fetchSetProperties())
   print(node.update())
   print(node.JSON['outdoor_temperature'])
   print(node.JSON.keys())
   print(node.outdoorTemperature)   
# aircon.on()
  # print(node.getAirflowVert())
   # print(node.getAutoDirection())
    #print(node.getSwingMode())

   # node.setSwingMode('vert')
   # node.setSwingMode('not-used')

   # node.setAirFlowVert('central')

   # print("Getting current operational parameters")
   # print(aircon.update())
   # aircon.setFanSpeed('medium-low')

   # print("Getting outdoor temperature")
   # print(aircon.getOutdoorTemperature())
