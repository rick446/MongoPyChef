import os
from hashlib import sha1
from binascii import b2a_hex

def nonce(bytes, printable=True):
    result = os.urandom(bytes)
    if printable:
        result = b2a_hex(result)
    return result

def cnonce(printable=True):
    if printable:
        return sha1(nonce(20)).hexdigest()
    else:
        return sha1(nonce(20)).digest()

