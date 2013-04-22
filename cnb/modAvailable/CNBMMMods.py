#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - mods
'''

# System imports
from cnb.cnbMatrix import CNBMatrix
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMMods(CNBMatrixModule):
    """

    """

    name = 'mods'
    usage = 'mods'
    desc = 'This cmd return a help page listing loaded modules'
    aliases = []
    isAdmin = True


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        oMatrix = CNBMatrix.getInstance()
        result = oMatrix.getMods(oMsg)
        return result
