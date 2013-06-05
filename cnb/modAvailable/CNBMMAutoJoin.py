#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - auto join
'''

from cnb.cnbManager import CNBManager
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMAutoJoin(CNBMatrixModule):
    """
    Let Chuck autojoin rooms on invitation
    """

    name = 'autojoin'
    usage = ''
    desc = 'This module let Chuck automatically join a room on invitation'
    aliases = []
    enProcessPattern = True
    enProcessCmd = False
    isAdmin = True

    # Constants
    GMAIL_ROOM_INVITE_TEXT = 'Click here to join: http://talkgadget.google.com'
    JAB_ROOM_INVITE_TEXT = 'invites you to the room'

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def checkPattern(self,oMsg):
        """
        """
        oMgr = CNBManager.getInstance()
        bAutoJoin = oMgr.getConfigCNB(oMsg.conId).get('bot', 'auto-join')
        if oMgr.getConfigCNB(oMsg.conId).has_option('bot', 'muc-domain'):
            sMucDomain = oMgr.getConfigCNB(oMsg.conId).get('bot', 'muc-domain')
        else:
            sMucDomain = ''
        if bAutoJoin \
            and oMsg.room != None \
            and oMsg.text != None \
            and oMsg.room.endswith(sMucDomain) \
            and ((oMsg.protocol == 'xmpp-gtalk' and self.GMAIL_ROOM_INVITE_TEXT in oMsg.text) \
                or (oMsg.protocol == 'xmpp' and self.JAB_ROOM_INVITE_TEXT+' '+oMsg.room in oMsg.text) \
                or (oMsg.protocol.startswith('irc'))):
            return True
        else:
            return False

    def processPattern(self, oMsg):
        result = ''
        oMgr = CNBManager.getInstance()
        result = oMgr.joinCNB(oMsg.conId,oMsg.room)
        return result

