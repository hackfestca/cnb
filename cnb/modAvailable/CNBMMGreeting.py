#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - greeting
'''

import os
import re
import sys
import random
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMGreeting(CNBMatrixModule):
    """

    """

    name = 'greeting'
    usage = ''
    desc = 'Detect some greeting message and reply one'
    enProcessCmd = False
    enProcessPattern = True

    SUP_MSG = ['sup', 'waza', 'hi', 'hello', 'sup', "what's up", 'salut']
    SUP_ANSWER = ['sup', 'waza', 'hi', 'hello', 'sup', "what's up", 'salut']

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        
    def __del__(self):
        pass

    def checkPattern(self,oMsg):
        if oMsg.text in self.SUP_MSG:
            return True
        else:
            return False
                
    def processPattern(self,oMsg):
        return self.SUP_ANSWER[random.randint(1,len(self.SUP_ANSWER)-1)]

