#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - encode
'''

# System imports
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMEncode(CNBMatrixModule):
    """

    """

    name = 'encode'
    usage = 'encode <MSG>'
    desc = 'Encode a string using rot13'
    aliases = []


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        stringList = oMsg.args[0::]
        for s in stringList:
            result = result + s.encode('rot13') + ' '
        return result

