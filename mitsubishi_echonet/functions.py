from .eojx import *
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



class Function:
    def _0EF0D6(edt):
        data = int.from_bytes(edt, 'big')
        edtnum = int((data & 0xff000000) / 0x1000000)
        # number of instances suggest that multiple instances per packet..
        # this may need a bit of a rethink...
        eojgc = int((data & 0x00ff0000) / 0x10000)
        eojcc = int((data & 0x0000ff00) / 0x100)
        eojci = int(data & 0x000000ff)

        # do something
        print("Group: " + EOJX_GROUP[eojgc])
        print("Code: " + EOJX_CLASS[eojgc][eojcc])
        print("Instance: " + str(eojci))

        return {
          "eojgc": eojgc,
          "eojcc": eojcc,
          "eojci": eojci
        }
    # Check status of Air Conditioner
    def _013080(edt):
        ops_value = int.from_bytes(edt, 'big')
        return {'status': ('On' if ops_value == 0x30 else 'Off')}

    # Check install location
    def _FF0081(edt):
        # ops_value = int.from_bytes(edt, 'little')
        return {'install_location': None}

    # Check standard version information
    def _FF0082(edt):
        # ops_value = int.from_bytes(edt, 'little')
        return {'version_info': None}

    # Check standard version information
    def _FF008A(edt):
        ops_value = int.from_bytes(edt, 'big')
        return {'manufacturer': ops_value}

    # Check status of Configured Temperature
    def _0130B3(edt):
        return {'set_temperature': int.from_bytes(edt, 'big')}

    # Check status of Room Temperature
    def _0130BB(edt):
        return {'room_temperature': int.from_bytes(edt, 'big')}

    # Check status of Fan speed
    def _0130A0(edt):
        op_mode = int.from_bytes(edt, 'big')
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


    def _0130AA(edt):
        op_mode = int.from_bytes(edt, 'big')
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
    def _0130B0(edt):
        op_mode = int.from_bytes(edt, 'big')
        values = {
           0x41: 'Automatic',
           0x42: 'Cooling',
           0x43: 'Heating',
           0x44: 'Dehumidification',
           0x45: 'Air circulator',
           0x40: 'Other'
        }
        return {'mode': values.get(op_mode, "Invalid setting" )}

    def _FF009E(edt):
        return {'setProperties': Function._FF009X(edt)}

    def _FF009F(edt):
        return {'getProperties': Function._FF009X(edt)}

    def _FF009X(edt):
        payload = []
        if len(edt) < 17:
            for i in range (1, len(edt)):
                payload.append(edt[i])
            return payload

        for i in range (1, len(edt)):
            code = i-1
            binary = '{0:08b}'.format(edt[i])[::-1]
            for j in range (0, 8):
                if binary[j] == "1":
                    EPC = (j+8) * 0x10 + code
                    payload.append(EPC)
        return payload
