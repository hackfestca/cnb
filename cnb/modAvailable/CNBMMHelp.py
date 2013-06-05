#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - help
'''

from cnb.cnbMatrix import CNBMatrix
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMHelp(CNBMatrixModule):
    """

    """

    name = 'help'
    usage = 'help [cmd]'
    desc = 'This cmd return a help page listing available commands'
    aliases = ['h']


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        oMatrix = CNBMatrix.getInstance()
        result = oMatrix.getHelp(oMsg)
        return result
