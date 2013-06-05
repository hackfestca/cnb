#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - websurf
'''

import os
import re
import sys
import random
import subprocess
from copy import copy
from cnb.cnbConfig import CNBConfig
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMWebSurf(CNBMatrixModule):
    """

    """

    name = 'surf'
    usage = 'surf URL'
    desc = 'Cmd used to dump web pages as text\
             URL: http://...'
    aliases = ['websurf']

    LYNX_CMD = ['lynx', '--dump']

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        
    def __del__(self):
        pass

    def processCmd(self, oMsg):

        result = ''
        if len(oMsg.args) > 0: 
            url = oMsg.args[0]
                
            cmd = copy(self.LYNX_CMD)
            cmd.append(url)
            self.log.info(str(cmd))
            result = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
        else:
            result = 'You must specify a URL'
        return result

