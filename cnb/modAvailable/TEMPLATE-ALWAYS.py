#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - <INSERT NAME HERE>

This file can be used as a template to create an "always" module.
Simply rename the class. Note that the class and the file name (excluding the .py suffix)
must be the same.
'''

from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMTemplateAlways(CNBMatrixModule): 
    """

    """

    name = ''
    usage = ''
    desc = 'This cmd do this and that'
    aliases = []
    enProcessAlways = True


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processAlways(self, oMsg):
        result = ''
        return result

