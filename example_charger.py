#!/usr/bin/env python3
import mitsubishi_echonet as mit

vehicle_charger = mit.ElectricVehicleCharger("1.1.1.1") #change IP address here.
print("Operational Status")
vehicle_charger.getOperationalStatus()

print("Set Properties")
vehicle_charger.fetchSetProperties()
print("Get Properties")
vehicle_charger.fetchGetProperties()
