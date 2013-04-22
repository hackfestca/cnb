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

class CNBMMGreeting(CNBMatrixModule):
    """

    """

    # Bot Config
    enProcessCmd = False
    enProcessPattern = True

    # Bot vars
    name = 'greeting'
    usage = ''
    desc = 'Detect some greeting message and reply one'
    SUP_MSG = ['sup', 'waza', 'hi', 'hello']
    SUP_ANSWER = ['sup', 'waza', 'hi', 'hello']

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
        if oMsg.text in self.SUP_MSG:
            return True
        else:
            return False
                
    #
    # Function: processPattern(oMsg)
    # Description: 
    #
    def processPattern(self,oMsg):
        return self.SUP_ANSWER[random.randint(1,len(self.SUP_ANSWER)-1)]

