#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - die
'''

# System imports
from cnb.cnbManager import CNBManager
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMDie(CNBMatrixModule):
    """

    """

    name = 'die'
    usage = 'die [DELAY]'
    desc = 'This cmd kill the bot'
    aliases = ['kill']
    hidden = True
    isAdmin = True


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        if len(oMsg.args) == 0:
            t = 0
        else:
            t = int(oMsg.args[0])
        oMgr = CNBManager.getInstance()
        oMgr.killCNB()
        result = ':('
        return result
