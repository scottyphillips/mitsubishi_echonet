#!/usr/bin/env python3
import mitsubishi_echonet as mit
import time

aircons = False
# Discover HVAC Echonet objects
while aircons == False:
    print("Discovering Air Conditioners..")
    aircons = mit.discover('Home air conditioner')

for aircon in aircons:
   print("Airconditioner {} available Get properties:".format(aircon.netif))
   #print(aircon.netif)
   print(aircon.fetchGetProperties())

   print("Airconditioner {} available Set properties:".format(aircon.netif))
   print(aircon.fetchSetProperties())

   aircon.on()
   aircon.setMode('dry')

   print("Getting current operational parameters")
   print(aircon.update())
   aircon.setFanSpeed('medium-low')
