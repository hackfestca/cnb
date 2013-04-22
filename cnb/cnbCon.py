#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This is the connector abstract class for CNB
'''

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from threading import Thread
from cnbConfig import CNBConfig

class CNBCon(Thread):
    """
    A "connector" is a connection made to a chat server such as IRC or XMPP. 
    
    """
    
    _bState = 'notstarted'
    """
    @ivar: State of a connection. 
    @type: string
    """

    _botConfig = None
    """
    @ivar: Config object 
    @type: ConfigParser
    """

    log = None
    """
    @ivar: Logging Object
    @type: logging
    """

    autoReconnect = True
    """
    @ivar: Determine if the connector must auto-reconnect on disconnect/failure
    @type: bool
    """

    def __init__(self,botConfig):
        Thread.__init__(self)
        self._botConfig = botConfig
        self.log = logging.getLogger(botConfig.get('bot', 'log-file'))
        self._configLogs(botConfig)
    
    def __del__(self):
        pass

    def _shutdown(self):
        pass

    def _quit(self):
        pass

    def _configLogs(self, botConfig):
        """
        This method configure the logs for this object. 

        Two handlers are used, one to print to stdout and one to log in a file. For file, TimedRotatingFileHandler is used to rotate the log file every day. 
        @param botConfig: Bot config to use to customize logging
        @type botConfig: ConfigParser
        """
        config = CNBConfig.getInstance()

        # Print output if not in daemon mode
        if not config.get('global', 'daemon'):
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(config.get('global', 'log-format')))
            self.log.addHandler(ch)

        # Write also to file
        fh = TimedRotatingFileHandler(os.path.join(config.get('global', 'log-dir'), \
                botConfig.get('bot', 'log-file')), \
                backupCount=0, \
                when='d', \
                interval=1)
        fh.setFormatter(logging.Formatter(config.get('global', 'log-format')))
        self.log.addHandler(fh)
       
        # Set log level
        if botConfig.get('bot', 'verbose') == '1':
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)
    
    def run(self):
        """
        This method is called when the thread is started. This must be overwritten in the connector class.
        """
        return 0

    def getState(self):
        """
        This method return the current state of the connector
        """
        return self._bState

    def setState(self, state):
        """
        This method change the state of the bot. 
        @param state: State to set
        @type state: String
        """
        self._bState = state

    def isRunning(self):
        """
        This method return True if the bot is running. Note: Running = the thread is started and not terminated yet.
        """
        if (self._bState in ['connecting','disconnecting','connected','disconnected','identifying','identified','joiningChannels', 'joiningRooms']):
            return True
        else:
            return False

    def startBot(self):
        """
        This method connect the bot
        """
        self.log.info('Setting state to: connecting')
        self.setState('connecting')

    def stopBot(self):
        """
        This method disconnect the bot
        """
        self.autoReconnect = False
        self.log.info('Setting state to: disconnecting')
        self.setState('disconnecting')

    def killBot(self):
        """
        This method kill the bot by terminating the thread.
        """
        self.log.info('Setting state to: dying')
        self.setState('dying')

    def getConfig(self):
        """
        This method return the bot config object.
        """
        return self._botConfig

    def isValidDomain(self, domain):
        """
        This function must be overwritten in the child classes.
        Determine if a domain is valid for this connection (Ex: for xmpp, there are muc domains (gmail.com) and user domains (talk.google.com))
        @param domain: The domain to check
        @type domain: string
        """
        return False

