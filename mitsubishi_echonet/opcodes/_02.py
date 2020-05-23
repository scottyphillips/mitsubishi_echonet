# Check status of Vehicle Charger
def _7E80(edt):
    ops_value = int.from_bytes(edt, 'big')
    return {'status': ('On' if ops_value == 0x30 else 'Off')}

# Check stat
