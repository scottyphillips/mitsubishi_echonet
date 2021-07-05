from ..eojx import *

def _F0D6(edt):
    data = int.from_bytes(edt, 'big')
    edtnum = int((data & 0xff000000) / 0x1000000)
    # number of instances suggest that multiple instances per packet..
    # this may need a bit of a rethink...
    eojgc = int((data & 0x00ff0000) / 0x10000)
    eojcc = int((data & 0x0000ff00) / 0x100)
    eojci = int(data & 0x000000ff)

    # do something
#    print("Group: " + EOJX_GROUP[eojgc])
#    print("Code: " + EOJX_CLASS[eojgc][eojcc])
#    print("Instance: " + str(eojci))

    return {
      "eojgc": eojgc,
      "eojcc": eojcc,
      "eojci": eojci
    }
