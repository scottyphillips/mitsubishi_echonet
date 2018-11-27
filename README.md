# mitsubishi_echonet
A library for interfacing with Mitsubishi HVAC with the Echonet lite protoocl over WiFi adaptors such as the MAC-568IF-E.

It is specifically designed for use with Home Assistant, and its functionality is limited to HVAC systems,
but it could be potentally extended for other Echonet applications and become a more general purpose library.

Similar implementations seem to be Node JS middleware running on Docker containers to interface into the MQTT API
however this is designed to be used as an old school library, no middleware, Node JS or Docker needed!


It is designed to work with Python 3.7 out of the box as that was the environment I was working on.

# Instructions
Because its not uploaded to PyPi yet, you need to cheat a little to get this working in Home Assistant

Basically, download the repo directly into the 'custom_components' folder. You now have the 'mitsubishi-echo' folder under custom components. Copy the 'mitsubishi.py' file that is inside the repot into 'custom_components/climate'. Now you should be set. 

Make sure you enable the ECHONET Lite service in the official Mitsubishi App.

In configuration.yaml add the following lines:

climate:
  - platform: mitsubishi
    ip_address: 1.2.3.4

Comments and suggestions are welcome!

# Thanks
Thanks to Jeffro Carr who inspired me to write my own native Python ECHONET library for
Home Assistant. Some ideas in his own repo got implemented in my own code. (https://github.com/jethrocarr/echonetlite-hvac-mqtt-service.git)

Also big thanks to Futomi Hatano for open sourcing a high quality and extremely well documented ECHONET Lite library in Node JS that  formed the basis of my reverse engineering efforts: https://github.com/futomi/node-echonet-lite

# Licence
This application is licensed under an MIT license, refer to LICENSE for details.
