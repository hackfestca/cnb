#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Chuck Norris Bot Matrix (his brain)
'''

# System imports
import os
import sys
import logging
import modEnabled
import collections
from logging.handlers import TimedRotatingFileHandler
from singleton import Singleton
from cnbConfig import CNBConfig
from cnbManager import CNBManager
from singleton import Singleton

@Singleton
class CNBMatrix():
    """
    This is Chuck Norris brain. The magic starts from here.
    The CNBIrcCon and CNBXmppCon classes, which manage connections to some chat servers, send their output to this class and then, an event or reply is trigerred.
    """

    # Constants
    MODULE_FROM = 'cnb.modEnabled'
    MSG_HELP_HEAD = 'Available commands:'
    MSG_HELP_TAIL = 'Type .help <command name> to get more info about that specific command.'
    MSG_HELP_UNDEFINED_COMMAND = 'That command is not defined.'
    LOG_FILE = 'cnb-matrix.log'
    UNKNOWN_MSG = ['yes', 'no', 'indeed', 'not sure...', 'hmmm', 'maybe', 'I would not say that', 'if you''re not nice, you will get a roundhouse kick to the face? are you crazy enough to challenge the chuck.', 'all the beatings i have done in sidekick were real', 'I cured that little bitch''s asthma']
    LOG_NICK = 'Chuck'

    _mods = {}
    """
    @ivar: Imported module list (indexed by name)
    @type: dict
    """

    _patterns = []
    """
    @ivar: List of pointers to imported pattern modules (indexed by getFullName()) 
    @type: List
    """

    _always = []
    """
    @ivar: List of pointers to imported always modules (indexed by getFullName())
    @type = List
    """

    log = None
    """
    @ivar: logging object
    @type = logging
    """

    def __init__(self):
        self.log = logging.getLogger(self.LOG_FILE)
        self._configLogs(self.LOG_FILE)
        self.registerEnMods()

    def __del__(self):
        self.freeMM()

    def _configLogs(self, sFile):
        """
        This method configure the logs for this object. 

        Two handlers are used, one to print to stdout and one to log in a file. For file, TimedRotatingFileHandler is used to rotate the log file every day. 

        @param sFile: Log file name
        @type sFile: string
        @todo: Set log level from config or user input
        """
        config = CNBConfig.getInstance()

        # Print output if not in daemon mode
        if not config.get('global', 'daemon'):
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(config.get('global', 'log-format')))
            self.log.addHandler(ch)

        # Write also to file
        fh = TimedRotatingFileHandler(\
            os.path.join(config.get('global', 'log-dir'), sFile), \
            backupCount=0, \
            when='d', \
            interval=1)
        fh.setFormatter(logging.Formatter(config.get('global', 'log-format')))
        self.log.addHandler(fh)
       
        # Must stay at DEBUG to log errors
        self.log.setLevel(logging.DEBUG)

    def _processMod(self, oMsg):
        """
        This method, called by connector specific methods (ex. processIrcMod, processXmppMod), determine if the user has access to call the module and then trigger an event or reply.
        @param oMsg: Message object containing a message, status change or a command.
        @type oMsg: CNBMessage
        """
        result = ''
        oMgr = CNBManager.getInstance()
        aAdminUsers = oMgr.getConfigCNB(oMsg.conId).get('bot', 'admins')
        oMod = self.getModuleFromCmd(oMsg.cmd)
        if oMod:
            # check for allowed users
            if self.isAllowed(oMod.users, oMsg.username, oMsg.domain):

                # check for admin modules
                if not oMod.isAdmin or (oMod.isAdmin and oMsg.username in aAdminUsers):
                    
                    # Is this a cmd?
                    if oMod.enProcessCmd:
                        result = oMod.processCmd(oMsg)

                else:
                    result = 'unauthorized (admin)'
            else:
                result = 'unauthorized (users)'
        else:
            # Can spot a pattern?
            for (p,c) in self._patterns:
                if c(oMsg):
                    result = p(oMsg)
                    if result != '':
                        break

            # Otherwise, check something else?
            if result == '':
                for v in self._always:
                    result = v(oMsg)
                    if result != '':
                        break

        # Logs
        if oMsg.text != '' and oMsg.replyTo != None:
            self.log.info(str(oMsg.replyTo) + ' -> ' + str(self.LOG_NICK) + '>' + str(oMsg.text))
        if result != '' and oMsg.replyTo != None:
            self.log.info(str(self.LOG_NICK) + ' -> ' + str(oMsg.replyTo) + '>' + str(result))

        return result

    def registerEnMods(self):
        """
        Import enabled modules, instanciate them and register them
        """
        modDir = modEnabled.__path__[0]
        self.log.info('Searching for modules in: ' + modDir)
        dirList = os.listdir(modDir)
        for fname in dirList:
            if fname != '..' and fname[0] != '.' and fname[:8] != '__init__' and fname[-3::] != 'pyc':
                try:
                    self.registerMod(fname)
                except Exception, e:
                    self.log.error('Could not register "' + fname + '"')
                    self.log.exception(e)

    def registerMod(self, modFileName):
        """
        This method register a single module
        @param oMatrixModule: Matrix module to import
        @type modFileName: string
        """
        sClass = modFileName.split('.')[0]
        try:
            oMod = __import__(self.MODULE_FROM + '.' + sClass, None, None, [self.MODULE_FROM])
        except ImportError, e:
            self.log.info('Failed to register module')
            self.log.exception(e)
            return 'Failed to register module'
        cClass = getattr(oMod,sClass)
        oMatrixModule = cClass(self.log)
        oMatrixModule.fileName = modFileName
        self._mods[oMatrixModule.name] = oMatrixModule

        # Bind process commands modules
        if oMatrixModule.enProcessCmd:
            self.log.info('Registered a command module: %s' % oMatrixModule.getFullName())

            for a in oMatrixModule.getAliases():
                self.log.info('Registered a command module: %s (alias of: %s)' % (a, oMatrixModule.getFullName()))
            
        # Bind pattern modules
        if oMatrixModule.enProcessPattern:
            self._patterns.append((oMatrixModule.processPattern, oMatrixModule.checkPattern))
            self.log.info('Registered a pattern module: %s' % oMatrixModule.getFullName())

        # Bind always module
        if oMatrixModule.enProcessAlways:
            self._always.append(oMatrixModule.processAlways)
            self.log.info('Registered an "always" module: %s' % oMatrixModule.getFullName())

        return 'Registered successfuly'

    def reloadMod(self, modFileName):
        sClass = modFileName.split('.')[0]
        reload(sys.modules[self.MODULE_FROM + '.' + sClass])

    def unregisterMod(self, modFileName):
        """
        This method unregister a single module
        @param oMatrixModule: Matrix module to unload
        @type modFileName: string
        """
        sClass = modFileName.split('.')[0]
        fullModName = self.MODULE_FROM + '.' + sClass
        i = self.getModuleIndex(sClass)
        oMatrixModule = self.getModule(sClass)
        if i:
            self.log.info('Unregistered a module: %s' % oMatrixModule.getFullName())
    
            if oMatrixModule.enProcessCmd:
                self.log.info('Unregistered a command module: %s' % oMatrixModule.getFullName())
            if oMatrixModule.enProcessPattern:
                i = self.getPatternIndex(sClass)
                self._pattern.pop(i)
                self.log.info('Unregistered a pattern module: %s' % oMatrixModule.getFullName())
            if oMatrixModule.enProcessAlways:
                i = self.getAlwaysIndex(sClass)
                self._pattern.pop(i)
                self.log.info('Unregistered an always module: %s' % oMatrixModule.getFullName())
   
            del self._mods[oMatrixModule.name]
            del oMatrixModule 
            oMatrixModule = None

            if fullModName in sys.modules:  
                self.log.info('Deleting sys.modules')
                del(sys.modules[fullModName]) 

            return 'Unregistered successfuly'
        else:
            self.log.info('Failed to unregister module: %s' % modFileName)
            return 'Module does not exist'

    def processXmppMod(self, oMsg):
        """
        Connector specific method: XMPP
        This method should be called by CNBXMPPCon class
        @param oMsg: A message sent to Chuck Norris
        @type oMsg: CNBMessage
        """
        if oMsg.protocol.startswith('xmpp') and (oMsg.text or oMsg.presType):
            try:
                result = self._processMod(oMsg)
            except Exception, e:
                self.log.exception(e)
                result = ''
        else:
            result = ''

        return result

    def processIrcMod(self, oMsg):
        """
        Connector specific method: IRC
        This method should be called by CNBIRCCon class
        @param oMsg: A message sent to Chuck Norris
        @type oMsg: CNBMessage
        """
        if oMsg.protocol.startswith('irc') and oMsg.text:
            try:
                result = self._processMod(oMsg)
                if result != None:
                    result = result.split("\n")
            except Exception, e:
                self.log.exception(e)
                result = ''
        else:
            result = ''

        return result

    # def processSipMod(self, oMsg):
    # ...

    # def processSkypeMod(self, oMsg):
    # ...

    def freeMM(self):
        """
        Free every imported module
        """
        for sName,oMod in self._mods.iteritems():
            self.log.debug('Freeing module: ' + oMod.name)
            self._mods[oMod.name] = None

    def isModule(self,name):
        """
        Determine if a module is imported from its name
        @param name: Name of a module to search
        @type name: string
        """
        for sName,oMod in self._mods.iteritems():
            if name == oMod.name or name in oMod.aliases:
                return True
        return False

    def isAllowed(self, acl, user, domain):
        if len(acl) == 0 or (len(acl) > 0 and domain in acl and user in acl[domain]):
            return True
        else:
            return False

    def getModule(self,name):
        """
        Get a module from its name
        @param name: Name of a module to return
        @type name: string
        """
        for sName,oMod in self._mods.iteritems():
            if name == oMod.name or name in oMod.aliases:
                return oMod
        return None

    def getModuleIndex(self,name):
        """
        Get a module index from its name
        @param name: Name of a module to return
        @type name: string
        """
        i = 0
        for sName,oMod in self._mods.iteritems():
            if name == oMod.name or name in oMod.aliases:
                return i
            i = i + 1
        return None

    def getPatternIndex(self,name):
        """
        Get a module index from its name
        @param name: Name of a module to return
        @type name: string
        """
        i = 0
        for oMod in self._pattern:
            if name == oMod.name or name in oMod.aliases:
                return i
            i = i + 1
        return None

    def getAlwaysIndex(self,name):
        """
        Get a module index from its name
        @param name: Name of a module to return
        @type name: string
        """
        i = 0
        for oMod in self._always:
            if name == oMod.name or name in oMod.aliases:
                return i
            i = i + 1
        return None

    def getModuleFromCmd(self,cmd):
        """
        Get a module from its command name. The main difference with "getModule()" is that a command has a prefix.
        @param name: Name of a module to return
        @type name: string
        """
        for sName,oMod in self._mods.iteritems():
            if cmd == oMod.getFullName() or cmd in oMod.getAliases():
                return oMod
        return None

    def getHelp(self,oMsg):
        """
        Returns a help string listing available commands.
        @param oMsg: Message sent to Chuck
        @type oMsg: CNBMessage
        """
        if len(oMsg.args) == 0:
            helpMsg = self.MSG_HELP_HEAD + "\n"
            for (sModName, oModule) in self._mods.iteritems():
                desc = str(oModule.desc).split("\n")[0]
                if not oModule.hidden and oModule.enProcessCmd:
                    if oModule.isAdmin:
                        helpMsg += "\t %s: \t\t [admin]%s\n" % (sModName, desc)
                    else:
                        helpMsg += "\t %s: \t\t [ std ]%s\n" % (sModName, desc)
            helpMsg += self.MSG_HELP_TAIL
        else:
            helpMsg = "Command Help Page: \n"
            cmd = oMsg.args[0]
            if cmd in self._mods:
                helpMsg += self._mods[cmd].desc + "\n"
                helpMsg += 'Usage: ' + self._mods[cmd].getUsage() + "\n"
            else:
                helpMsg = self.MSG_HELP_UNDEFINED_COMMAND
        return helpMsg

    def getMods(self,oMsg):
        """
        Returns a help string listing loaded modules
        @param oMsg: Message sent to Chuck
        @type oMsg: CNBMessage
        """
        helpMsg = self.MSG_HELP_HEAD + "\n"
        for (sModName, oModule) in self._mods.iteritems():
            desc = str(oModule.desc).split("\n")[0]
            if oModule.enProcessCmd:
                helpMsg += "\t %s: \t\t [  cmd  ]%s\n" % (sModName, desc)
            elif oModule.enProcessPattern:
                helpMsg += "\t %s: \t\t [pattern]%s\n" % (sModName, desc)
            elif oModule.enProcessAlways:
                helpMsg += "\t %s: \t\t [always ]%s\n" % (sModName, desc)
        helpMsg += self.MSG_HELP_TAIL
        return helpMsg

