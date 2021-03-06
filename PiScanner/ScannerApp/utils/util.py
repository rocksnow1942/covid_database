from warnings import warn
import base64
from dateutil import parser
from dateutil import tz

def warnImplement(funcname,ins):
    warn(f"Implement <{funcname}> in {ins.__class__.__name__}")


def indexToGridName(index,grid=(12,8),direction='top'):
    "convert 0-95 index to A1-H12,"
    rowIndex = "ABCDEFGHIJKLMNOPQRST"[0:grid[1]]
    rowIndex = rowIndex if direction == 'top' else rowIndex[::-1]
    row = index//grid[0] + 1
    col = index - (row-1) * grid[0] + 1
    rowM = rowIndex[row-1]
    return f"{rowM}{col}"


def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)
    

def parseISOTime(ts):
    "turn mongo time stamp to python datetime object."
    dt = parser.parse(ts)
    return dt.astimezone(tz.tzlocal())