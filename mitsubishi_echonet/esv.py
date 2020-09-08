# ------------------------------------------------------------------
# ESV
# ------------------------------------------------------------------
GETC = 			0x60
SETC = 			0x61
GET  = 			0x62
INFREQ =		0x63
SETGET = 		0x6E
SETRES =		0x71
GETRES =		0x72
INF =			0x73
INFC = 			0x74
INFC_RES =		0x7A
SETGET_RES =	0x7E
SETI_SNA = 		0x50
SETC_SND =		0x51
GET_SNA = 		0x52
INF_SNA = 		0x53
SETGET_SNA =	0x5E

MODES = {
	'auto':  	0x41,
	'cool':  	0x42,
	'heat':  	0x43,
	'dry':  	0x44,
	'fan_only':	0x45,
	'other': 	0x40
}

FAN_SPEED = {
	'auto':	        0x41,
	'minimum':  	0x31,
	'low':  		0x32,
	'medium-low': 	0x33,
	'medium':		0x34,
	'medium-high': 	0x35,
	'high':			0x36,
	'very-high':    0x37,
	'max':			0x38
}

AIRFLOW_HORIZ = {
    'rc-right':             0x41,
    'left-lc':              0x42,
    'lc-center-rc':         0x43,
    'left-lc-rc-right':     0x44,
    'right':                0x51,
    'rc':                   0x52,
    'center':               0x54,
    'center-right':         0x55,
    'center-rc':            0x56,
    'center-rc-right':      0x57,
    'lc':                   0x58,
    'lc-right':             0x59,
    'lc-rc':                0x5A,
    'left':                 0x60,
    'left-right':           0x61,
    'left-rc':              0x62,
    'left-rc-right':        0x63,
    'left-center':          0x64,
    'left-center-right':    0x65,
    'left-center-rc':       0x66,
    'left-center-rc-right': 0x67,
    'left-lc-right':        0x69,
    'left-lc-rc':           0x6A
}

AIRFLOW_VERT = {
    'upper':            0x41,
    'upper-central':    0x44,
    'central':          0x43,
    'lower-central':    0x45,
    'lower':            0x42
}

AUTO_DIRECTION = {
    'auto':         0x41,
    'non-auto':     0x42,
    'auto-vert':    0x43,
    'auto-horiz':   0x44
}

    # Automatic swing of air flow direction setting

SWING_MODE = {
    'not-used':     0x31,
    'vert':         0x41,
    'horiz':        0x42,
    'vert-horiz':   0x43
}

ESV_CODES = {
	0x60: {'name': 'GetC', 'description': 'Property value write request (no response required)'},
	0x61: {'name': 'SetC', 'description': 'Property value write request (response required)'},
	0x62: {'name': 'Get', 'description': 'Property value read request'},
	0x63: {'name': 'INF_REQ', 'description': 'Property value notification request'},
	0x6E: {'name': 'SetGet', 'description': 'Property value write & read request'},
	0x71: {'name': 'Set_Res', 'description': 'Property value Property value write response'},
	0x72: {'name': 'Get_Res' , 'description': 'Property value read response'},
	0x73: {'name': 'INF' , 'description': 'Property value notification'},
	0x74: {'name': 'INFC', 'description': 'Property value notification (response required)'},
	0x7A: {'name': 'INFC_Res' , 'description': 'Property value notification response'},
	0x7E: {'name': 'SetGet_Res' , 'description': 'Property value write & read response'},
	0x50: {'name': 'SetI_SNA', 'description': 'Property value write request (response not possible)'},
	0x51: {'name': 'SetC_SNA' , 'description': 'Property value write request (response not possible)'},
	0x52: {'name': 'Get_SNA', 'description': 'Property value read (response not possible)'},
	0x53: {'name': 'INF_SNA', 'description': 'Property value notification (response not possible)'},
    0x5E: {'name': 'SetGet_SNA', 'description': 'Property value write & read (response not possible)'}
}
