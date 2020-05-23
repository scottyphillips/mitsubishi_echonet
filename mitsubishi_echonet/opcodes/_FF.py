# Check install location
def _0081(edt):
    # ops_value = int.from_bytes(edt, 'little')
    return {'install_location': None}
# Check standard version information
def _0082(edt):
    # ops_value = int.from_bytes(edt, 'little')
    return {'version_info': None}

# Check standard version information
def _008A(edt):
    ops_value = int.from_bytes(edt, 'big')
    return {'manufacturer': ops_value}

def _009E(edt):
    return {'setProperties': _009X(edt)}

def _009F(edt):
    return {'getProperties': _009X(edt)}

def _009X(edt):
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
