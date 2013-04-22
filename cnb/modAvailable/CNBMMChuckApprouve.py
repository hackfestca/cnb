#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module
'''

# System imports
import os
import re
import sys
import random
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMChuckApprouve(CNBMatrixModule):
    """

    """

    # Bot Config
    enProcessCmd = False
    enProcessPattern = True

    # Bot vars
    name = 'approuve'
    usage = ''
    desc = 'Approuve an affirmation when the bot detect 3x "k" messages'
    _nbKMsg = 0
    IRC_CHAT, IRC_GROUPCHAT = 'privmsg', 'pubmsg'
    XMPP_CHAT, XMPP_GROUPCHAT = 'chat', 'groupchat'
    KKK_REPLY = 'approuved'
    KKK_MSG = 'k'
    KKK_NB_MAX = 3

    #
    # Function: __init__()
    # Description: 
    #
    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        
    #
    # Function: __del__()
    # Description: 
    #
    def __del__(self):
        pass

####################
# Public Functions #
####################
    #
    # Function: checkPattern(oMsg)
    # Description: Should return True or False
    #
    def checkPattern(self,oMsg):
        if oMsg.text == self.KKK_MSG and oMsg.protocol.startswith('xmpp') and oMsg.type == self.XMPP_GROUPCHAT:
            return True
        elif oMsg.text == self.KKK_MSG and oMsg.protocol == 'irc' and oMsg.type == self.IRC_GROUPCHAT:
            return True
        else:
            return False
                
    #
    # Function: processPattern(oMsg)
    # Description: 
    #
    def processPattern(self,oMsg):
        self._nbKMsg = self._nbKMsg + 1
        self.log.debug('NbKMsg: ' + str(self._nbKMsg))
        if self._nbKMsg > self.KKK_NB_MAX:
            #reply = 'k'
            #self.send_simple_reply(mess, reply)
            self._nbKMsg = 0
            return self.KKK_REPLY
        else:
            return ''

