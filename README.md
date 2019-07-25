# Mitsubishi Echonet

A library for interfacing with Mitsubishi HVAC with the ECHONET-lite protocol
over WiFi adaptors such as the MAC-568IF-E.

It is specifically designed for use with Home Assistant, and its functionality
is limited to HVAC systems, but it could be potentially extended for other
ECHONET-lite applications and become a more general purpose library.

Similar implementations seem to be Node JS middleware running on Docker
containers to interface into the MQTT API however this is designed to be used
as a straight up library, no middleware, Node JS or Docker containers needed!

It is designed to work with Python 3.7 out of the box as
that was the environment I was working on.

## Instructions

Simplest way to install is to use pip:

```
pip install mitsubishi_echonet
```

## Basic usage
### Discover a list of HVAC using:
```python
aircons = mit.discover('Home air conditioner')
aircon = aircons[0]
```

### Turn HVAC on or off:
```python
aircon.on()
aircon.off()
aircon.getOperationalStatus()
{'status': 'Off'}
```

### Set or Get a HVACs target temperature
```python
aircon.setOperationalTemperature(25)
aircon.getOperationalTemperature()
{'set_temperature': 25}
```

### Set or Get a HVACs mode of operation:
```python
supported modes =  'auto', 'cool', 'heat', 'dehumidify', 'fan_only', 'other'

aircon.setMode('cool')
aircon.getMode()
{'mode': 'cool'}
```
### Set or Get a HVACs fan speed:

Note - your HVAC may not support all fan speeds.
```python
supported modes = 'auto', 'minimum', 'low', 'medium-Low', 'medium', 'medium-high', 'high', 'very high', 'max'

aircon.setFanSpeed('medium-high')
aircon.getFanSpeed()
{'fan_speed': 'medium-high'}
```
### Get HVAC attributes at once:
```python
aircon.update()
{'status': 'On', 'set_temperature': 25, 'fan_speed': 'Medium-High', 'room_temperature': 25, 'mode': 'Cooling'}
```
## Using the library with Home Assistant

There are two files under /bin
'example.py' is an executable Python3 script that will discover your
Mitsubishi HVAC and play with some settings.

'/custom_components/mitsubishi/climate.py' is for use with Home Assistant (v0.89+)
Copy the '/mitsubishi/climate.py' (including folder) into your 'custom_components'

In configuration.yaml add the following lines:
```yaml
climate:
  - platform: mitsubishi
    ip_address: 1.2.3.4
```
## Fine tuning fan settings.
Optionally, you can also specify what fan settings work with your specific
HVAC system. If no fan speeds are configured, the system will default to 'low'
and 'medium-high'. Just delete the ones you dont need.
Note: if you are on 0.95 use ```fan_list``` not ```fan_modes```

```yaml
climate:
  - platform: mitsubishi
    ip_address: 192.168.1.6
    name: "mitsubishi_ducted"
    fan_modes:
      - 'minimum'
      - 'low'
      - 'medium-low'
      - 'medium'
      - 'medium-high'
      - 'high'
      - 'very-high'
      - 'max'
```

## Help! Home Assistant could not run the module?

When I was playing around with this I had difficulty getting hass.io to install
the library from pip. No idea why, but eventually I found the correct
combination to get it to work as it is supposed to.

However, there is a workaround:

1. Clone the repo
2. Copy the 'mitsubishi_echonet' subfolder directly out of the repo and
into the 'custom_components' directory.
3. Flip the comments on the following lines in climate.py:
```
import mitsubishi_echonet as mit
# import custom_components.mitsubishi_echonet as mit
```
Make sure you enable the ECHONET Lite service in the official Mitsubishi App.

Comments and suggestions are welcome!

## Thanks

Thanks to Jeffro Carr who inspired me to write my own native Python ECHONET
library for Home Assistant. I could not get his Node JS Docker container
to work properly on Hass.io :-)
Some ideas in his own repo got implemented in my own code.
(https://github.com/jethrocarr/echonetlite-hvac-mqtt-service.git)

Also big thanks to Futomi Hatano for open sourcing a high quality and
extremely well documented ECHONET Lite library in Node JS that formed
the basis of my reverse engineering efforts.
(https://github.com/futomi/node-echonet-lite)

## License

This application is licensed under an MIT license, refer to LICENSE for details.
