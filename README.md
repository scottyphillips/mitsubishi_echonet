# Mitsubishi Echonet

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]


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
{'status': 'off'}
```

### Set or Get a HVACs target temperature
```python
aircon.setOperationalTemperature(25)
aircon.getOperationalTemperature()
{'set_temperature': 25}
```

### Set or Get a HVACs mode of operation:
```python
supported modes =  'auto', 'cool', 'heat', 'dry', 'fan_only', 'other'

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
{'status': 'On', 'set_temperature': 25, 'fan_speed': 'medium-high', 'room_temperature': 25, 'mode': 'cooling'}
```
## Using this library with Home Assistant

NOTE: For Home Assistant users there is now a dedicated repo for the related Home Assistant 'Mitsubishi' custom component that makes use of this Python library:
(https://github.com/scottyphillips/mitsubishi_hass)

The custom component examples in the /bin directory will be removed from this
repo at a later release and this repo will focus solely on the Python library.

'example.py' in the /bin directory gives you an idea how to drive the
HVAC directly from Python using this library.

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

***
[mitsubishi_echonet]: https://github.com/scottyphillips/mitsubishi_echonet
[releases-shield]: https://img.shields.io/github/release/scottyphillips/mitsubishi_echonet.svg?style=for-the-badge
[releases]: https://github.com/scottyphillips/mitsubishi_echonet/releases
[license-shield]:https://img.shields.io/github/license/scottyphillips/mitsubishi_echonet?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/RgKWqyt?style=for-the-badge
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/Maintainer-Scott%20Phillips-blue?style=for-the-badge
