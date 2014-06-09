# -*- coding: utf-8 -*-
#
#  privacyIDEA is a fork of LinOTP
#  May 08, 2014 Cornelius Kölbel
#  License:  AGPLv3
#  contact:  http://www.privacyidea.org
#
#  Copyright (C) 2010 - 2014 LSE Leading Security Experts GmbH
#  License:  AGPLv3
#  contact:  http://www.linotp.org
#            http://www.lsexperts.de
#            linotp@lsexperts.de
#  HMAC-OTP (RFC 4226)
#  Copyright (C) LSE Leading Security Experts GmbH, Weiterstadt
#  Written by Max Vozeler <max.vozeler@lsexperts.de>
"""
  Description:  HOTP basic functions
"""
  
import hmac
import logging
import struct

from hashlib import sha1
from privacyidea.lib.log import log_with

import sys
(ma, mi, _, _, _,) = sys.version_info
pver = float(int(ma) + int(mi) * 0.1)


log = logging.getLogger(__name__)


class HmacOtp():

    def __init__(self, secObj=None, counter=0, digits=6, hashfunc=sha1):
        self.secretObj = secObj
        self.counter = counter
        self.digits = digits
        self.hashfunc = hashfunc


    def hmac(self, counter=None, key=None):
        #log.error("hmacSecret()")
        counter = counter or self.counter

        data_input = struct.pack(">Q", counter)
        if key == None:
            dig = str(self.secretObj.hmac_digest(data_input, self.hashfunc))
        else:
            if pver > 2.6:
                dig = hmac.new(key, data_input, self.hashfunc).digest()
            else:
                dig = hmac.new(key, str(data_input), self.hashfunc).digest()

        return dig


    def truncate(self, digest):
        offset = ord(digest[-1:]) & 0x0f

        binary = (ord(digest[offset + 0]) & 0x7f) << 24
        binary |= (ord(digest[offset + 1]) & 0xff) << 16
        binary |= (ord(digest[offset + 2]) & 0xff) << 8
        binary |= (ord(digest[offset + 3]) & 0xff)

        return binary % (10 ** self.digits)


    def generate(self, counter=None, inc_counter=True, key=None):
        counter = counter or self.counter

        otp = str(self.truncate(self.hmac(counter=counter, key=key)))
        """  fill in the leading zeros  """
        sotp = (self.digits - len(otp)) * "0" + otp
        if inc_counter:
            self.counter = counter + 1
        return sotp

    @log_with(log)
    def checkOtp(self, anOtpVal, window, symetric=False):
        res = -1
        start = self.counter
        end = self.counter + window
        if symetric == True:
            # changed window/2 to window for TOTP
            start = self.counter - (window)
            start = 0 if (start < 0) else start
            end = self.counter + (window)

        log.debug("OTP range counter: %r - %r" % (start, end))
        for c in range(start , end):
            otpval = self.generate(c)
            log.debug("calculating counter %r: %r %r"
                      % (c, anOtpVal, otpval))
            #log.error("otp[%d]: %s : %s",c,otpval,anOtpVal)

            if (unicode(otpval) == unicode(anOtpVal)):
                # log.debug("Match Pin: %s : %d : %s",otpval,c,anOtpVal)
                res = c
                break
        #return -1 or the counter
        return res

#eof##########################################################################
