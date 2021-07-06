#!/usr/bin/env python3
import mitsubishi_echonet as mit
import time

# Discover Echonet instances
instances = mit.discover()
print(instances)

# create a HVAC instance object
aircon = mit.HomeAirConditioner("192.168.1.6")

# return all the property maps for the HVAC instance
print(aircon.getAllPropertyMaps())

# aircon.on()
# aircon.setMode('heat')

# aircon.setFanSpeed('medium-low')

# aircon.setOperationalTemperature(21)

# Home Assistant friendly updates
print(aircon.update())
