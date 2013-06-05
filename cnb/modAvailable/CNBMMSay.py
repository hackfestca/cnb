#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - say
'''

from cnb.cnbManager import CNBManager
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMSay(CNBMatrixModule):
    """

    """

    name = 'say'
    usage = 'say USER|ROOM|CHAN MSG'
    desc = 'This cmd let you send a message to someone'
    aliases = []
    isAdmin = True

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        if len(oMsg.args) > 1:
            sUser = str(oMsg.args[0])
            sMsg = str(' '.join(oMsg.args[1::]))
            oConMgr = CNBManager.getInstance()
            result = oConMgr.sayCNB(oMsg.conId,sUser,sMsg)
        else:
            result = 'Specify a user and a message. Check help for more.'
        return result

