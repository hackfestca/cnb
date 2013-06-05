#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module
'''

import sys
from StringIO import StringIO
import argparse 
#from optparse import OptionParser

class CNBMatrixModule():
    """
    Definition of a Matrix Module. This class should be inherited in every module class.
    """
    
    isAdmin = False
    """ 
    @ivar: Determine if the module can be accessed by admins only
    @type: bool
    """

    replyToUserOnly = False
    """ 
    @ivar: Determine if the module reply to the user only, even if the cmd was send on a room/chan
    @type: bool
    """

    hidden = False
    """ 
    @ivar: Determine if the module is hidden. An hidden module won't show up in the help page. 
    @type: bool
    """

    enProcessCmd = True
    """ 
    @ivar: Determine if the module is processed from a command. If yes, the module is accessed by sending specific commands to bot (ex: .fact would reply a Chuck Norris fact). 
    @type: bool
    """

    enProcessPattern = False
    """ 
    @ivar: Determine if the module is processed from a pattern. If yes, the module is accessed by detecting some patterns on chat rooms or user behaviors (ex: 3x "k" message will output a "approuved")
    @type: bool
    """

    enProcessAlways = False
    """ 
    @ivar: Determine if the module is processed at anytime. This could be useful for statistics or behavior analysis. 
    @type: bool
    """

    log = None
    """ 
    @ivar: log object
    @type: bool
    """

    prefix = '.'
    """ 
    @ivar: Module prefix
    @type: String
    """

    name = ''
    """ 
    @ivar: Module name
    @type: String
    """

    fileName = ''
    """
    @ivar: Module file name (including .py)
    @type: string
    """

    usage = ''
    """ 
    @ivar: Module usage help page
    @type: String
    """

    desc = ''
    """ 
    @ivar: Module description
    @type: String
    """

    parser = None
    """
    @ivar: Input messages parser. This should be set for cmd module only.
    @type: OptionParser
    """

    aliases = []
    """ 
    @ivar: Module aliases (ex: For .fact module, we could add .facts, .chuckfact, .chuckfacts, etc.)
    @type: List
    """

    users = {}
    """
    @ivar: List of users that are allowed to use the module. when the array is empty, everyone can use the module.
    @type = hash table
    @note: syntax: {'<domain>': ['user1', 'user2', 'user3'], ... }
    """

    def __init__(self,oLog):
        self.log = oLog
        if not self._checkIntegrity():
            self.log.info('The "' + self.name + '" module is invalid')

    def __del__(self):
        pass

    def _checkIntegrity(self):
        """
        Check if the integrity of the module. For example, some attributes must be set correctly for the module to work.
        """
        # If the module is processed from a command
        if self.enProcessCmd:
            # A name must be set
            if self.name == '':
                return False
    
            # A usage must be set
            #if self.usage == '':
            #    return False
    
            # A description must be set
            if self.desc == '':
                return False

        # The module must be processable from either a command or a pattern
        if self.enProcessCmd == False and self.enProcessPattern == False:
            return False
        
        # Modules can be pattern and cmd based. Uncomment to for force one type at a time.
        #if self.enProcessCmd == True and self.enProcessPattern == True:
        #    return False
        return True

    def _initOptParser(self, bHelpOption=True):
        """
        Initialize the option parser. Call this method only if you want to manage arguments with OptionParser
        Note that it also overwrite the usage attribute.
        """
        #usage = 'usage: ' + self.prefix + self.usage
        #self.parser = CNBArgumentParser(usage=usage, add_help=bHelpOption)
        self.parser = CNBArgumentParser(prog=self.prefix+self.name,add_help=bHelpOption)

    def getParsedArgs(self, args):
        strIO = StringIO()
        sys.stdout = strIO
        try:
            args = self.parser.parse_args(args)
        except TypeError:
            self.log.info('Type Error')
        res = strIO.getvalue()
        sys.stdout = sys.__stdout__
        return (args, res)

    def getFullName(self):
        """
        Get full name of a module (including prefix)
        """
        if self.enProcessCmd:
            return self.prefix + self.name
        else:
            return self.name

    def getUsage(self):
        """
        Get usage of a module (including prefix)
        """
        if self.parser:
            strIO = StringIO()
            sys.stdout = strIO
            self.parser.print_help()
            res = strIO.getvalue()
            sys.stdout = sys.__stdout__
            return res
        else:
            return self.prefix + self.usage

    def getAliases(self):
        """
        Get a complete list of the module aliases
        """
        aList = []
        for a in self.aliases:
            aList.append(self.prefix + a)
        return aList

    def checkPattern(self,oMsg):
        """
        For pattern mode only: Check if the message satisfy the pattern. This method must return true or false
        @param oMsg: Message to process
        @type oMsg: CNBMessage
        """
        return False

    def processCmd(self,oMsg):
        """
        For command mode only: This method should be overwritten to process something
        @param oMsg: Message to process
        @type oMsg: CNBMessage
        """
        return ''

    def processPattern(self,oMsg):
        """
        For pattern mode only: This method should be overwritten to process something when checkPattern() return True
        @param oMsg: Message to process
        @type oMsg: CNBMessage
        """
        return ''

    def processAlways(self,oMsg):
        """
        This method should be overwritten to process something on every message
        @param oMsg: Message to process
        @type oMsg: CNBMessage
        """
        return ''

class CNBArgumentParser(argparse.ArgumentParser):
    """
    Source: http://stackoverflow.com/questions/1885161/how-can-i-get-optparses-optionparser-to-ignore-invalid-options
    """
    def error(self, msg):
        print msg
        pass
