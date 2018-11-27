#!/usr/bin/env python3
from mitsubishi_echonet import lib_mitsubishi as mit

# Discover HVAC Echonet objects
aircon = mit.Discover()[0]

# Returns dict of HVAC status
aircon.Update()

# Sets the fan speed
aircon.SetFanSpeed('Medium-High')

# Sets the mode
aircon.SetMode('Heating')

# Sets the temperature
aircon.SetOperationalTemperature(18)

# Turns on the Air Conditioner:
aircon.On()

# Returns dict of HVAC status
aircon.Update()

# Turns off the Air Conditioner:
aircon.Off()
