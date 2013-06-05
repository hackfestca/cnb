#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - hash
'''

import hashlib
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMHash(CNBMatrixModule):
    """

    """

    name = 'hash'
    usage = 'hash TYPE PLAIN_TEXT'
    desc = 'Hash any plain text into a hash (md5, sha1, sha224, sha256, sha384, sha512)'
    aliases = []


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        supTypes = {'md5': hashlib.md5,
                        'sha1': hashlib.sha1,
                        'sha224': hashlib.sha224,
                        'sha256': hashlib.sha256,
                        'sha384': hashlib.sha384,
                        'sha512': hashlib.sha512
                        }
        if len(oMsg.args) == 1:
           result = supTypes['md5'](oMsg.args[0]).hexdigest() 

        elif len(oMsg.args) > 1:
            hashType = oMsg.args[0].lower()
            text = ' '.join(oMsg.args[1::])
            if hashType in supTypes:
                result = result + ' ' + supTypes[hashType](text).hexdigest()
            else:
                result = 'Type not supported'
        else:
            result = 'This cmd takes at least 2 arguments, check help'
        return result

