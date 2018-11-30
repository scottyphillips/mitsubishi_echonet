#!/usr/bin/env python3
import mitsubishi_echonet as mit
import time

aircon = False
# Discover HVAC Echonet objects
while aircon == False:
    print("Discovering Air Conditioner..")
    aircon = mit.discover()[0]

print (aircon.fetchSetProperties())
# Returns dict of HVAC status
# aircon.off()
# time.sleep(1)
# Sets the fan speed
aircon.setFanSpeed('Medium-High')
time.sleep(1)

# aircon.getOperationalStatus()
# time.sleep(1)


# Sets the mode

aircon.setMode('Heating')
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
