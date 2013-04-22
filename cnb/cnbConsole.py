#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Chuck Norris Bot Console
"""

# System imports
import os
import sys
import inspect
import logging
from time import sleep
from threading import Thread
from logging.handlers import TimedRotatingFileHandler

# Local imports
from cnbConnectorManager import CNBConnectorManager
from cnbManager import CNBManager
from cnbConfig import CNBConfig

# Constants
CMD_PREFIX = ''

def consolecmd(*args, **kwargs):
    """
    This function is a signature used to identify command methods in the Console class
    """
    def decorate(func, hidden=False, name=None, type=None):
        """
        Set some attribute to a method
        """
        setattr(func, '_console_cmd', True)
        setattr(func, '_console_type', type)
        setattr(func, '_console_hidden', hidden)
        setattr(func, '_console_cmd_name', name or func.__name__)
        return func

    if len(args):
        return decorate(args[0], **kwargs)
    else:
        return lambda func: decorate(func, **kwargs)

class CNBConsole(Thread):
    """
    This class is the cli admin console of CNB
    """

    # Constants
    MSG_HELP_TAIL = 'Type help <command name> to get more info about that specific command.'
    MSG_HELP_UNDEFINED_COMMAND = 'That command is not defined.'
    MSG_TOP_OF_HELP = ''
    MSG_BOTTOM_OF_HELP = ''

    _cmds = {}
    """ 
    @ivar: This hash table contains the list of commands the console can handle in main mode
    @type: hashtable
    """

    _cmdsXmpp = {}
    """ 
    @ivar: This hash table contains the list of commands the console can handle in XMPP mode
    @type: hashtable
    """

    _cmdsIrc = {}
    """ 
    @ivar: This hash table contains the list of commands the console can handle in IRC mode
    @type: hashtable
    """

    _conList = []
    """ 
    @ivar: This array contains the list of manageable connectors
    @type: List
    """
    
    _curConId = None
    """ 
    @ivar: This is the currently managed connector ID
    @type: int
    """

    _bState = 'notstarted'
    """ 
    @ivar: State of the console
    @type: String
    """

    def __init__(self):
        Thread.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        self._configLogs('cnb-console.log')
    
        config = CNBConfig.getInstance()
        for name, value in inspect.getmembers(self):
            if inspect.ismethod(value) and getattr(value, '_console_cmd', False) and getattr(value, '_console_type') == None:
                name = getattr(value, '_console_cmd_name')
                self.log.info('Registered console command: %s' % name)
                self._cmds[name] = value

            if inspect.ismethod(value) and getattr(value, '_console_cmd', False) and getattr(value, '_console_type') == 'xmpp':
                name = getattr(value, '_console_cmd_name')
                self.log.info('Registered xmpp console command: %s' % name)
                self._cmdsXmpp[name] = value

            if inspect.ismethod(value) and getattr(value, '_console_cmd', False) and getattr(value, '_console_type') == 'irc':
                name = getattr(value, '_console_cmd_name')
                self.log.info('Registered irc console command: %s' % name)
                self._cmdsIrc[name] = value

    def __del__(self):
        self.killConsole()

    def _shutdown(self):
        """
        This method is called when the console is killed.
        """
        self.log.info('Shutting down...')

    def _configLogs(self,sFile):
        """
        This method configure the logs for this object. 

        Two handlers are used, one to print to stdout and one to log in a file. For file, TimedRotatingFileHandler is used to rotate the log file every day. 

        @param sFile: Log File
        @type sFile: string
        """
        config = CNBConfig.getInstance()

        # Print output if not in daemon mode
        if not config.get('global', 'daemon'):
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(config.get('global', 'log-format')))
            self.log.addHandler(ch)

        # Write also to file
        fh = TimedRotatingFileHandler(os.path.join(config.get('global', 'log-dir'), sFile), backupCount=0, when='d', interval=1)
        fh.setFormatter(logging.Formatter(config.get('global', 'log-format')))
        self.log.addHandler(fh)
        
        self.log.setLevel(logging.INFO)

    def run(self):
        """
        Console main loop
        """
        self.log.info('Serving forever...')
        self.startConsole()
        while self.isRunning():
            try:
                self.processUserInput()
            except KeyboardInterrupt:
                self.log.info('CNBConsole stopped by user request. shutting down.')
                break
            sleep(1)
        
        # When loop is done, shutdown
        self._shutdown()
        return 0
    
    def getState(self):
        """
        This method return the current state of the console
        """
        return self._bState

    def setState(self, state):
        """
        This method set the current state of the console
        """
        self._bState = state

    def isRunning(self):
        """
        Determine if the console is running
        """
        if (self._bState in ['running']):
            return True
        else:
            return False

    def startConsole(self):
        """
        Start the console
        """
        self.setState('running')

    def stopConsole(self):
        """
        Stop the console
        """
        self.setState('stopped')

    def killConsole(self):
        """
        This method kill the console. Note: kill = the thread is terminated. This may close the program.
        """
        self._autoReconnect = False
        self.stopConsole()

    def processUserInput(self):
        """
        This method wait for raw_input() and process the user command
        """
        if self._curConId:
            curBot = self._getInstFromId(self._curConId)
            conMsg = 'ChuckConsole-' + curBot.config.get('bot', 'type') + '-' + str(curBot.config.get('bot', 'id')) + '>'
        else:
            conMsg = 'ChuckConsole>'

        text = raw_input(conMsg)

        if ' ' in text:
            cmd, args = text.split(' ', 1)
        else:
            cmd, args = text, ''
        self.log.debug("*** cmd = %s" % cmd)
        
        if not self._curConId and self._cmds.has_key(cmd):
            self.log.info(self._cmds[cmd](cmd, args))
        elif self._curConId and curBot.get('global', 'type') == 'xmpp' and self._cmdsXmpp.has_key(cmd):
            self.log.info(self._cmdsXmpp[cmd](cmd, args))
        elif self._curConId and curBot.get('global', 'type') == 'irc' and self._cmdsIrc.has_key(cmd):
            self.log.info(self._cmdsIrc[cmd](cmd, args))

#####################
# Console Functions #
#####################
    @consolecmd(name=CMD_PREFIX+'help')
    def _help(self, cmd, args):
        """
        Returns a help string listing available options
        Usage: help [commands]
        Details: 
        """ 
        if not args:
            if self.__doc__:
                description = self.__doc__.strip()
            else:
                description = 'Available commands:'

            usage = '\n'.join(sorted([
                '%s\t\t%s' % (name, (command.__doc__ or '(undocumented)').strip().split('\n', 1)[0])
                for (name, command) in self._cmds.iteritems() if not command._console_hidden
            ]))
            usage = '\n\n'.join(filter(None, [usage, self.MSG_HELP_TAIL]))
        else:
            description = ''
            if args in self._cmds:
                usage = (self._cmds[args].__doc__ or 'undocumented').strip()
            else:
                usage = self.MSG_HELP_UNDEFINED_COMMAND

        return '\n\n'.join(filter(None, [self.MSG_TOP_OF_HELP, description, usage, self.MSG_BOTTOM_OF_HELP]))

    @consolecmd(name=CMD_PREFIX+"createInstance")
    def _createInstance(self, cmd, args):
        """
        """
        pass

    @consolecmd(name=CMD_PREFIX+"deleteInstance")
    def _deleteInstance(self, cmd, args):
        """
        """
        pass
    
    @consolecmd(name=CMD_PREFIX+"startInstance")
    def _startInstance(self, cmd, args):
        """Start an instance of the bot
        Usage: startInstance INSTANCE_ID
        Details: """

        # Validation and var initialisation
        if len(args.split(' ')) == 1:
            instId = args.split(' ')[0]
        else:
            instId = None
        
        # Core
        if instId:
            i = self._getInstFromId(instId)
            if i:
                i.startBot()
                result = 'Bot started'
            else:
                result = 'Could not find instance number ' + str(instId)
        else:
            result = 'This function needs 1 argument. You entered ' + str(len(args.split(' '))) + ' arguments'
        return '\n' + result
    
    @consolecmd(name=CMD_PREFIX+"stopInstance")
    def _stopInstance(self, cmd, args):
        """Stop an instance of the bot
        Usage: stopInstance INSTANCE_ID
        Details: """

        # Validation and var initialisation
        if len(args.split(' ')) == 1:
            instId = args.split(' ')[0]
        else:
            instId = None
        
        # Core
        if instId:
            i = self._getInstFromId(instId)
            if i:
                i.stopBot()
                result = 'Bot stopped'
            else:
                result = 'Could not find instance number ' + str(instId)
        else:
            result = 'This function needs 1 argument. You entered ' + str(len(args.split(' '))) + ' arguments'
        return '\n' + result
    
    @consolecmd(name=CMD_PREFIX+"saveInstance")
    def _saveInstance(self, cmd, args):
        """
        """
        pass
    
    @consolecmd(name=CMD_PREFIX+"loadInstance")
    def _loadInstance(self, cmd, args):
        """
        """
        pass

    @consolecmd(name=CMD_PREFIX+"setInstance")
    def _setInstance(self, cmd, args):
        """Set an instance of the bot to manage it
        Usage: setInstance INSTANCE_ID
        Details: """
        # Validation and var initialisation
        if len(args.split(' ')) == 1:
            instId = args.split(' ')[0]
        else:
            instId = None

        if instId and self._getInstFromId(instId):
            self._curConId = instId
            result = 'Instance set to ' + str(instId)
        else:
            result = 'Could not find instance id ' + str(instId)

        return result 
    
    @consolecmd(name=CMD_PREFIX+"listInstances")
    def _listInstances(self, cmd, args):
        """List instances
        Usage: listInstances
        Details: Print a list of instances and their status"""

        # Core
        result = 'ID\tCONFIG-FILE\tUSERNAME\tSTATE\n'
        for bot in self._conList:
            result = result + str(bot.config.get('bot', 'id')) + '\t' + bot.config.get('bot', 'config-file') + '\t' + bot.config.get('bot', 'username') + '\t' + bot.getState() + '\n'
        return '\n' + result

    @consolecmd(name=CMD_PREFIX+"setVar")
    def _setVar(self, cmd, args):
        """
        """
        pass

    @consolecmd(name=CMD_PREFIX+"start")
    def _startChuck(self, cmd, args):
        """ Start CNB
        Usage: start
        Details: Start this program"""
        result = ''
        result += 'Starting...'
        oMgr = CNBManager.getInstance()
        oMgr.startCNB()
        return '\n' + result

    @consolecmd(name=CMD_PREFIX+"stop")
    def _stopChuck(self, cmd, args):
        """ Stop CNB
        Usage: stop
        Details: Stop this program (become idle)"""
        result = ''
        result += 'Stopping...'
        oMgr = CNBManager.getInstance()
        oMgr.stopCNB()
        return '\n' + result

    @consolecmd(name=CMD_PREFIX+"exit")
    def _exitChuck(self, cmd, args):
        """ Exit the console
        Usage: exit
        Details: Exit this program"""
        result = ''
        result += 'Exiting...'
        oMgr = CNBManager.getInstance()
        oMgr.killCNB()
        return '\n' + result

    @consolecmd(name=CMD_PREFIX+"forceexit")
    def _forceExitChuck(self, cmd, args):
        """ Exit the console
        Usage: exit
        Details: Exit this program"""
        result = ''
        sys.exit(0)
        return '\n' + result

   # TO BE MIGRATED
    @consolecmd(name=CMD_PREFIX+"saymuc")
    def _sayMUCChuck(self, cmd, args):
        """ Make ChuckNorris say something to a Multi-User Chat
        Usage: say USER|ID MESSAGE
        Details: Make the bot say something to a muc
          USER: Email address of the user
          ID: Auto generated id starting with a '$'
          MESSAGE: Anything
        """
        if len(args.split(' ')) >= 2:
            user, msg = args.split(' ', 1)
            if user[0] == '$':
                user = self.getContactFromId(self.currentInst, user)
            self._bot.send(user, msg, None, 'groupchat')
            result  = "Msg sent to %s" % user
        else:
            result = "This cmd takes at least 2 arguments, check help"
        return result

    @consolecmd(name=CMD_PREFIX+"join")
    def _joinRoomChuck(self, cmd, args):
        """ Make ChuckNorris join a room 
        Usage: join ROOM
        Details: Make the bot join a room so he can talk with people"""
        room = str(args)
        if room != '' and ' ' not in room:
            self._bot.join_room(args)
            result  = "Joined room: %s" % room
        else:
            result = "This cmd takes 1 argument, check help"
        return result

    @consolecmd(name=CMD_PREFIX+"aujoin")
    def _autoJoinRoomChuck(self, cmd, args):
        """ Make ChuckNorris join a room automaticaly
        Usage: autojoin
        Details: Make the bot automaticaly join a room on invitation so he can talk with people"""
        autojoin = str(args)
        if autojoin == 'off':
            self._bot.autojoin = False
            result  = "Changed autojoin to False"
        elif autojoin == 'on':
            self._bot.autojoin = True
            result  = "Changed autojoin to True"
        else:
            result = "This cmd takes 1 argument, check help (Current value: " + str(self._bot.autojoin) + ")"
        return result

    @consolecmd(name=CMD_PREFIX+"verbose")
    def _verboseChuck(self, cmd, args):
        """ Change the loglevel of the bot
        Usage: verbose on|off
        Details: Change the loglevel between logging.INFO (off) and logging.DEBUG (on)"""
        loglevel = str(args)
        if loglevel == 'off':
            self._bot.log.setLevel(logging.INFO)
            result  = "Changed log level to INFO"
        elif loglevel == 'on':
            self._bot.log.setLevel(logging.DEBUG)
            result  = "Changed log level to DEBUG"
        else:
            result = "This cmd takes 1 argument, check help (Current value: " + str(self._bot.log.getEffectiveLevel()) + ")"
        return result

    @consolecmd(name=CMD_PREFIX+"contact")
    def _contactChuck(self, cmd, args):
        """ View/update contact list
        Usage: contact list|update
        Details: 
            - list: Show a list of constacts with their IDs
            - update: Get the result of self.conn.Roster.getRoster() and update self.roster & self.contacts arrays"""
        action = str(args)
        if action == 'list':
            for contactId in self._bot.contacts:
                self.log.info('%s - %s' % (contactId, self._bot.contacts[contactId]))
            result  = ""
        elif action == 'update':
            self._bot.updateRosters()
            result  = "Roster list updated"
        else:
            result = "This cmd takes 1 argument, check help"
        return result

#
# Console XMPP commands Functions
#
    @consolecmd(name=CMD_PREFIX+'help', type='xmpp')
    def _help(self, cmd, args):
        """
        Returns a help string listing available options
        Usage: help [commands]
        Details: 
        """ 

    @consolecmd(name=CMD_PREFIX+'exit', hidden=True, type='xmpp')
    def _exitXMPP(self, cmd, args):
        """ 
        """
        self._curConId = None
        return ''

    @consolecmd(name=CMD_PREFIX+"say", type='xmpp')
    def _sayXmppChuck(self, cmd, args):
        """ Make ChuckNorris say something to someone
        Usage: say USER|ID MESSAGE
        Details: Make the bot say something to someone
          USER: Email address of the user
          ID: Auto generated id starting with a '$'
          MESSAGE: Anything
        """
        # Validation
        if len(args.split(' ')) >= 2:
            user, msg = args.split(' ', 1)
        else:
            user, msg = None, None

        # Core
        if user:
            if user[0] == '$':
                user = self.getContactFromId(self._curConId, user)
        
            curBot = self._getInstFromId(self._curConId)
            curBot.send(user, msg)
            result  = "Msg sent to %s" % user
        else:
            result = "This cmd takes at least 2 arguments, check help"
        return result


    @consolecmd(name=CMD_PREFIX+"join", type='xmpp')
    def _joinXmppChuck(self, cmd, args):
        """
        """
        pass

    @consolecmd(name=CMD_PREFIX+"contact", type='xmpp')
    def _contactXmppChuck(self, cmd, args):
        """
        """
        pass
#
# Console IRC commands Functions
#
    @consolecmd(name=CMD_PREFIX+'help', type='irc')
    def _help(self, cmd, args):
        """
        Returns a help string listing available options
        Usage: help [commands]
        Details: 
        """ 

    @consolecmd(name=CMD_PREFIX+'exit', hidden=True, type='irc')
    def _exitIRC(self, cmd, args):
        """ 
        """
        self._curConId = None
        return ''
