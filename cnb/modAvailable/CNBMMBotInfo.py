#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - bot info
'''

# System imports
import os
from datetime import datetime
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMBotInfo(CNBMatrixModule):
    """

    """

    name = 'botinfo'
    usage = 'botinfo [arg]'
    desc = 'Print some information about the bot (current datetime, current user, OS, etc.)'
    aliases = []


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass


    def processCmd(self, oMsg):
        result = ''
        if len(oMsg.args) > 0:
            subCmds = {'os': self._getOs,
                       'load': self._getLoadAvg,
                       'date': self._getDate,
                       'time': self._getTime,
                       'user': self._getUser
                      }
            if oMsg.args[0] in subCmds:
                result = subCmds[oMsg.args[0]]()
            else:
                result = 'Invalid sub cmd'
        else:
            result = 'OS: ' + self._getOs() + "\n"
            result += 'Load: ' + self._getLoadAvg() + "\n"
            result += 'Date: ' + self._getDate() + "\n"
            result += 'Time: ' + self._getTime() + "\n"
            result += 'User: ' + self._getUser() + "\n"
        return result

    def _getOs(self):
        """
        Displays the OS version
        """
        result = open('/proc/version').read().strip()
        return result
    
    def _getLoadAvg(self):
        """
        Displays the load average
        """
        result = open('/proc/loadavg').read().strip()
        return result
    
    def _getDate(self):
        """
        Displays current server date
        """
        return str(datetime.now().strftime("%Y-%m-%d"))

    def _getTime(self):
        """
        Displays current server time
        """
        return str(datetime.now().strftime("%H:%M"))

    def _getUser(self):
        """
        Tells you your username
        """
        return os.getlogin()
