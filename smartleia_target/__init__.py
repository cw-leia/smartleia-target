"""
Here is detailed the python API of the `smartleia` package.
"""


import ctypes
import threading
import time

from enum import Enum, IntEnum, IntFlag
from typing import List, Optional, Union

import serial
import serial.tools.list_ports

__all__ = [
    "TargetController",
]

__version__ = "1.0.0"

name = "smartleia_target"


import logging

import smartleia as SL

import binascii

from Crypto.Cipher import AES

import time

INS_SET_KEY         = 0x11 #load 16 byte, 24 byte, or 32 byte key
INS_SET_PLAINTEXT        = 0x12 #load  plaintext to be encrypted, size <= 128 bytes - see below - multiple of a 16 byte AES block
INS_GET_RESULT      = 0x13 #return the result of the operation
INS_GO              = 0x14 #start the operation
INS_GET_KEY         = 0x15 #return the loaded key
INS_GET_PLAINTEXT        = 0x16 #return loaded  plaintext

INS_SET_DIR         = 0x17 #takes an argument: 0x00 is ENCRYPT, 0x01 is DECRYPT
DIR_ENC             = 0x00
DIR_DEC             = 0x01

INS_SET_TYPE        = 0x18 #takes an argument: 0x00 is AES_HARD, 0x01 is AES_SOFT
TYPE_AES_HARD       = 0x00
TYPE_AES_SOFT       = 0x01

MAX_PAYLOAD_SIZE    = 128

AES_TEST_VECTOR_KEY = "2b7e151628aed2a6abf7158809cf4f3c"
AES_TEST_VECTOR_PLAINTEXT = "6bc1bee22e409f96e93d7e117393172a"
AES_TEST_VECTOR_CIPHERTEXT = "3ad77bb40d7a3660a89ecaf32466ef97"

DEBUG=0

class TargetController(SL.LEIA):

    _name= 'LEIA Java Smartcard Target controller'
    
    connectStatus = False
    key = AES_TEST_VECTOR_KEY
    plaintext = AES_TEST_VECTOR_PLAINTEXT
    ciphertext = AES_TEST_VECTOR_CIPHERTEXT

    def __init__(self, solo=True):
        self.solo = solo
        SL.LEIA.__init__(self)

    def getStatus(self):
        return self.connectStatus

    def dis(self):
    
        """Disconnect from target"""
        self.close()
        self.connectStatus = False

    def con(self, scope=None, **kwargs):
        """Connect to target"""
        
        try:
            self.open()
            self.connectStatus = True

        except:
            self.dis()
            raise


    def sendMyAPDU(self, cla, ins, p1, p2, tx_data=None, recv=0, send_le=0):
        """Send APDU to SmartCard, get Response"""
        # Compute recv on two bytes
        resp = None
        ab = recv // 256
        cd = recv % 256
        if send_le != 0:
            # Adapt the case where we need an extended APDU
            send_le = 1 if recv < 256 else 2
        # Crafting the APDU
        if tx_data:
            apdu = SL.APDU(cla=cla, ins=ins, p1=p1, p2=p2, lc=len(tx_data),  data=tx_data, le=recv, send_le=send_le)
        else:
            apdu = SL.APDU(cla=cla, ins=ins, p1=p1, p2=p2, lc=0x00, le=recv, send_le=send_le)
        if DEBUG:
            print(apdu)            
        # send the APDU    
        resp = self.send_APDU(apdu)
        if DEBUG:
            print(resp)
        assert hex(resp.sw1) == hex(0x90)
        assert hex(resp.sw2) == hex(0x00)
        return resp


    @property
    def output_len(self):
        """The length of the output expected from the crypto algorithm (in bytes)"""

        return len(self.getExpected())

    @output_len.setter
    def output_len(self, length):
        #FIXME
        return 16

    def _con(self, scope=None):
        self.con()

    def reinit(self):
        pass

    def select_applet(self, applet=[0x45, 0x75, 0x74, 0x77, 0x74, 0x75, 0x36, 0x41, 0x70, 0x80]):
        """Select the target applet"""

        return self.sendMyAPDU(cla=0x00, ins=0xA4, p1=0x04, p2=0x00, tx_data=applet, recv=0, send_le=0)

    def setModeEncrypt(self):
        """Set target to do encryption"""

        return self.sendMyAPDU(cla=0x00, ins=INS_SET_DIR, p1=0x00, p2=0x00, recv=0,  tx_data=DIR_ENC, send_le=0)

    def setModeDecrypt(self):
        """Set target to do decryption"""

        return self.sendMyAPDU(cla=0x00, ins=INS_SET_DIR, p1=0x00, p2=0x00, recv=0, tx_data=DIR_DEC, send_le=0)

    def setTypeHard(self):
        """Set target to do encryption"""

        return self.sendMyAPDU(cla=0x00, ins=INS_SET_TYPE, p1=0x00, p2=0x00, recv=0, tx_data=TYPE_AES_HARD, send_le=0)

    def setTypeSoft(self):
        """Set target to do encryption"""

        return self.sendMyAPDU(cla=0x00, ins=INS_SET_DIR, p1=0x00, p2=0x00, recv=0, tx_data=TYPE_AES_SOFT, send_le=0)

    def checkEncryptionKey(self, key):
        """System 'suggests' encryption key, and target modifies it if required because e.g. hardware has fixed key"""
        
        return self.sendMyAPDU(cla=0x00, ins=INS_GET_KEY, p1=0x00, p2=0x00, recv=0x00)


    def checkPlaintext(self, plaintext):
        """System suggests plaintext; target modifies as required"""

        return self.sendMyAPDU(cla=0x00, ins=INS_GET_PLAINTEXT, p1=0x00, p2=0x00, recv=0x00)


    def loadEncryptionKey(self, key=AES_TEST_VECTOR_KEY):
        """Load desired encryption key"""

        self.key = key
        return self.sendMyAPDU(cla = 0x00, ins=INS_SET_KEY, p1=0x00, p2=0x00, tx_data=bytearray.fromhex(self.key), recv=0, send_le=0)


    def loadInput(self,  plaintext=AES_TEST_VECTOR_PLAINTEXT):
        """Load input plaintext"""
        self.plaintext =  plaintext.ljust(32,chr(0x00))[:32]
        return self.sendMyAPDU(cla = 0x00, ins=INS_SET_PLAINTEXT, p1=0x00, p2=0x00, tx_data=bytearray.fromhex(self. plaintext), recv=0, send_le=0)


    def isDone(self):
        """If encryption takes some time after 'go' called, lets user poll if done"""

        return True

    def readOutput(self):
        """Read result"""

        return self.sendMyAPDU(cla = 0x00, ins=INS_GET_RESULT, p1=0x00, p2=0x00, tx_data=0, recv=0)

    def go(self):
        """Do Encryption"""
        return self.sendMyAPDU(cla = 0x00, ins=INS_GO, p1=0x00, p2=0x00, recv=0)

    def keyLen(self):
        """Length of key system is using"""

        return len(self.key)

    def textLen(self):
        """Length of the plaintext used by the system"""

        return len(self. plaintext)

    def getExpected(self):
        """Based on key & text get expected"""

        if AES and hasattr(self, 'key') and hasattr(self, 'plaintext') and self. plaintext and self.key:
            ciphertext = AES.new(bytes.fromhex(self.key), AES.MODE_ECB)
            ct = ciphertext.encrypt(bytes.fromhex(self. plaintext))
            ct = bytearray(ct)
            return ct
        else:
            return None

    def _dict_repr(self):
        raise NotImplementedError("Must define target-specific properties.")

    def __repr__(self):
        return util.dict_to_str(self._dict_repr())

    def __str__(self):
        return self.__repr__()


