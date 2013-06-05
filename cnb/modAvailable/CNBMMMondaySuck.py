#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - mondaysuck
'''

from cnb.cnbManager import CNBManager
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMMondaySuck(CNBMatrixModule):
    """

    """

    name = 'mondaysuck'
    usage = 'mondaysuck'
    desc = 'Create a chan/room so people can "security react" :)'
    aliases = ['tuesdaysuck', 'wednesdaysuck', 'thursdaysuck', 'fridayrock']
    users = {'gmail.com': ['martin.dube', 'nostalgeek', 'sigmens', 'patoff', 'marcandremeloche', 'psyker156', 'mr.un1k0d3r']}

    GTALK_INVITE_LIST = ['martin.dube@gmail.com','nostalgeek@gmail.com','sigmens@gmail.com','patoff@gmail.com',\
                        'marcandremeloche@gmail.com','psyker156@gmail.com','mr.un1k0d3r@gmail.com']

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass
    
    def processCmd(self, oMsg):
        """
        @todo: Invite only people that are not in the room
        """
        result = ''
        if oMsg.protocol == 'xmpp-gtalk':
            oMgr = CNBManager.getInstance()
            sRoom = oMgr.getConfigCNB(oMsg.conId).get('bot', 'monday-suck-room')
            oMgr.inviteCNB(oMsg.conId,self.GTALK_INVITE_LIST,sRoom)
        else:
            result = 'not'
        return result

