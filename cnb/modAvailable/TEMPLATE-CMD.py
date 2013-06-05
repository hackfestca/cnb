#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - <INSERT NAME HERE>

This file can be used as a template to create a "cmd" module.
Simply rename the class. Note that the class and the file name (excluding the .py suffix)
must be the same.
'''

from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMTemplateCmd(CNBMatrixModule): 
    """

    """

    name = ''
    usage = ''
    desc = 'This cmd do this and that'
    aliases = []


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        return result

