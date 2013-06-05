#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - Approuve
'''

import random
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMApprouve(CNBMatrixModule):
    """

    """

    name = 'approuve'
    usage = ''
    desc = 'Approuve an affirmation when the bot detect 4x "k" messages'
    enProcessCmd = False
    enProcessPattern = True

    _nbKMsg = 0
    IRC_CHAT, IRC_GROUPCHAT = 'privmsg', 'pubmsg'
    XMPP_CHAT, XMPP_GROUPCHAT = 'chat', 'groupchat'
    KKK_REPLY = ['Approuved', 'I approuve this message', 'I agree', 'Yarrr', 'Certainement.']
    KKK_MSG = ['k', 'kk', 'kkk', 'ok', 'okay', 'oki', 'confirmed', 'agree', 'i agree', 'indeed', \
                'y', 'yes', 'yep', 'yup', 'yarrr', 'affirmative', 'certainement.', 'oui', "D'accord"]
    KKK_NB_MAX = 4

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        
    def __del__(self):
        pass

    def checkPattern(self,oMsg):
        if str(oMsg.text).lower() in self.KKK_MSG \
            and ((oMsg.protocol.startswith('xmpp') and oMsg.type == self.XMPP_GROUPCHAT)\
            or (oMsg.protocol.startswith('irc') and oMsg.type == self.IRC_GROUPCHAT)):
            return True
        else:
            return False
                
    def processPattern(self,oMsg):
        self._nbKMsg = self._nbKMsg + 1
        self.log.debug('NbKMsg: ' + str(self._nbKMsg))
        if self._nbKMsg > self.KKK_NB_MAX:
            self._nbKMsg = 1
            return self.KKK_REPLY[random.randint(1, len(self.KKK_REPLY)-1)]
        else:
            return ''

