#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - Tether Fail
'''

# System imports
import collections
from datetime import datetime
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMTetherFail(CNBMatrixModule):
    """

    """

    name = 'tether'
    usage = 'tether'
    desc = 'This module count the number of deconnection of a user in a day'
    aliases = ['tetherfail']
    enProcessCmd = True
    enProcessPattern = True

    eventList = []
    AVAILABLE, AWAY, CHAT, DND, XA, OFFLINE = None, 'away', 'chat', 'dnd', 'xa', 'unavailable'

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def _getFailureCounts(self, today=True):
        d = {}
        for e in self.eventList:
            if (today and e['datetime'].date() == datetime.today().date()) or not today:
                if d.has_key(e['jid']):
                    d[e['jid']] += 1
                else:
                    d[e['jid']] = 1
        sl = sorted(d.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        return sl

    def checkPattern(self,oMsg):
        if oMsg.presType == self.OFFLINE:
            #print 'Type' + oMsg.presType
            #print 'Show' + oMsg.presShow
            #print 'Status' + oMsg.presStatus
            #print 'From' + oMsg.jid
            return True
        else:
            return False

    def processPattern(self, oMsg):
        result = ''
        self.eventList.append({'datetime': datetime.now(), 'jid': oMsg.jid.split('/')[0]})
        return result

    def processCmd(self, oMsg):
        if len(oMsg.args) > 0 and oMsg.args[0] == 'all':
            result = "List of users who went unavailable since startup:\n"
            failList = self._getFailureCounts(False)
        else:
            result = "List of users who went unavailable since the begining of the day:\n"
            failList = self._getFailureCounts()

        for jid,count in failList:
            result += jid + ': ' + str(count) + "\n"
        return result

