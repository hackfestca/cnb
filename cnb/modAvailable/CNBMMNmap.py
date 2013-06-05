#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - nmap
'''

import subprocess
from copy import copy
from time import sleep, strftime
from cnb.cnbConfig import CNBConfig
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMNmap(CNBMatrixModule):
    """
    @todo: Validate hostsnames before launching
    @todo: Make all arguments possible
    """

    name = 'nmap'
    usage = 'nmap TARGET1 [TARGET2 [TARGET]]>'
    desc = 'This cmd launch a nmap -A -P0 -iL on the specified target'
    aliases = []
    isAdmin = True

    NMAP_FILE = 'nmap/scan'
    NMAP_CMD = ['nmap', '-A', '-P0', '-iL']

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        if len(oMsg.args) > 0:
            targetList = oMsg.args
            
            # Create temporary file
            oConfig = CNBConfig.getInstance()
            sLogDir = oConfig.get('global', 'log-dir')
            tmpFileName = sLogDir + self.NMAP_FILE + strftime("%Y-%m-%d_%H%M%S") + '.txt'
            fh = open(tmpFileName,"w")
            for h in targetList:
                fh.write(h + "\n")
            fh.close()
                
            cmd = copy(self.NMAP_CMD)
            cmd.append(tmpFileName)
            self.log.info(str(cmd))
            result = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

            fh = open(tmpFileName,"a")
            fh.write('Command: ' + str(cmd))
            fh.write('User: ' + oMsg.username)
            fh.writelines(result)
            fh.close()
        else:
            result = "This cmd takes at least 1 arguments, check help"
        return result

