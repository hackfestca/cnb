#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - join
'''

from cnb.cnbManager import CNBManager
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMJoin(CNBMatrixModule):
    """

    """

    name = 'join'
    usage = 'join CHAN|ROOM'
    desc = 'This cmd let Chuck join a chan/room'
    aliases = []
    isAdmin = True

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        if len(oMsg.args) > 0:
            oConMgr = CNBManager.getInstance()
            result = oConMgr.joinCNB(oMsg.conId,oMsg.args[0])
        else:
            result = 'Specify a chan/room name. Check help for more.'
        return result


