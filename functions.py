from mitsubishi_echonet  import eojx
# EF0D6 will decode EDT0 to derive the node data which could be useful to
# create a echonet object of a particular type. Most likely called
# through the node creation process.
#
# Profile class group 0E
#
# - EDT0     |Property value data             |01 ..|01 01 30 01
#  - NUM     |Total number of instances       |01   |1
#  - EOJ     |ECHONET Lite object specificat..|01 ..|01 30 01
#    - EOJX1 |Class group code                |01   |Air conditioner-related device class group
#    - EOJX2 |Class code                      |30   |Home air conditioner class
#    - EOJX3 |Instance code                   |01   |1

def _0EF0D6(data):
    data = int.from_bytes(data, 'big')
    edtnum = int((data & 0xff000000) / 0x1000000)
    # number of instances suggest that multiple instances per packet..
    # this may need a bit of a rethink...
    eojgc = int((data & 0x00ff0000) / 0x10000)
    eojcc = int((data & 0x0000ff00) / 0x100)
    eojci = int(data & 0x000000ff)

    # do something
    print("Group: " + eojx.GROUP[eojgc])
    print("Code: " + eojx.CLASS[eojgc][eojcc])
    print("Instance: " + str(eojci))

    return {
      "eojgc": eojgc,
      "eojcc": eojcc,
      "eojci": eojci
    }

# Check status of Air Conditioner
def _013080(data):
    ops_value = int.from_bytes(data, 'little')
    return {'status': ('On' if ops_value == 0x30 else 'Off')}

# Check status of Configured Temperature
def _0130B3(data):
    return {'set_temperature': int.from_bytes(data, 'big')}

# Check status of Room Temperature
def _0130BB(data):
    return {'room_temperature': int.from_bytes(data, 'big')}

def _0130A0(data):
    op_mode = int.from_bytes(data, 'big')
    values = {
       0x41: 'Automatic',
       0x31: 'Minimum',
       0x32: 'Low',
       0x33: 'Medium-Low',
       0x34: 'Medium',
       0x35: 'Medium-High',
       0x36: 'High',
       0x37: 'Very High',
       0x38: 'Max'
    }
    return {'fan_speed': values.get(op_mode, "Invalid setting")}


def _0130AA(data):
    op_mode = int.from_bytes(data, 'big')
    print(hex(op_mode))
    values = {
      0x40: 'Normal operation',
      0x41: 'Defrosting',
      0x42: 'Preheating',
      0x43: 'Heat removal'
      }
    # return({'special':hex(op_mode)})
    return {'special_setting': values.get(op_mode, "Invalid setting")}

# Operation mode
def _0130B0(data):
    op_mode = int.from_bytes(data, 'big')
    values = {
       0x41: 'Automatic',
       0x42: 'Cooling',
       0x43: 'Heating',
       0x44: 'Dehumidification',
       0x45: 'Air circulator',
       0x40: 'Other'
    }
    return {'mode': values.get(op_mode, "Invalid setting" )}
