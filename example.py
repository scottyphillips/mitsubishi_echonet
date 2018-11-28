#!/usr/bin/env python3
from mitsubishi_echonet import lib_mitsubishi as mit
import time

# Discover HVAC Echonet objects
aircon = mit.discover()[0]

mit.getPropertyMaps("192.168.1.11", 0x01, 0x30, 0x01)
# Returns dict of HVAC status
# aircon.update()
# time.sleep(1)
# Sets the fan speed
# aircon.setFanSpeed('Medium-High')
# time.sleep(1)
# Sets the mode

# aircon.setMode('Heating')
# time.sleep(1)

# Sets the temperature
# aircon.setOperationalTemperature(18)
# time.sleep(1)



# Turns on the Air Conditioner:
# aircon.On()

# Returns dict of HVAC status
# aircon.Update()

# Turns off the Air Conditioner:
# aircon.Off()
