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
	'Automatic':		0x41,
	'Cooling':  		0x42,
	'Heating':  		0x43,
	'Dehumidification': 0x44,
	'Air circulator':	0x45,
	'Other': 			0x40
}

FAN_SPEED = {
	'Automatic':	0x41,
	'Minimum':  	0x31,
	'Low':  		0x32,
	'Medium-Low': 	0x33,
	'Medium':		0x34,
	'Medium-High': 	0x35,
	'High':			0x36,
	'Very High':    0x37,
	'Max':			0x38
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
