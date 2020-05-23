# Check status of Air Conditioner
def _3080(edt):
    ops_value = int.from_bytes(edt, 'big')
    return {'status': ('On' if ops_value == 0x30 else 'Off')}

# Check status of Configured Temperature
def _30B3(edt):
    return {'set_temperature': int.from_bytes(edt, 'big')}

# Check status of Room Temperature
def _30BB(edt):
    return {'room_temperature': int.from_bytes(edt, 'big')}

# Check status of Outdoor Temperature
def _30BE(edt):
    return {'outdoor_temperature': int.from_bytes(edt, 'big')}

# Check status of Fan speed
def _30A0(edt):
    op_mode = int.from_bytes(edt, 'big')
    values = {
       0x41: 'auto',
       0x31: 'minimum',
       0x32: 'low',
       0x33: 'medium-low',
       0x34: 'medium',
       0x35: 'medium-high',
       0x36: 'high',
       0x37: 'very-high',
       0x38: 'max'
    }
    return {'fan_speed': values.get(op_mode, "Invalid setting")}


def _30AA(edt):
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
def _30B0(edt):
    op_mode = int.from_bytes(edt, 'big')
    values = {
       0x41: 'auto',
       0x42: 'cool',
       0x43: 'heat',
       0x44: 'dry',
       0x45: 'fan_only',
       0x40: 'other'
    }
    return {'mode': values.get(op_mode, "Invalid setting" )}
