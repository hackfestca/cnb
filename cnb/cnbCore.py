#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This is the core class of CNB. 
'''

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from time import sleep
from threading import Thread
from cnbConnectorManager import CNBConnectorManager
from cnbManager import CNBManager
from cnbConfig import CNBConfig
from cnbMatrix import CNBMatrix
from cnbConsole import CNBConsole

class CNBCore(Thread):
    """
    This class manage the main loop, all the states and this loop logs. 
    """

    _bState = 'notstarted'
    """ 
    @ivar: This is the state var of the main loop. For example, the ``startCNB()`` method will set this var to "starting".
    @Note: Possible values are: ['notstarted','starting','running','stopping','stopped','dying']
    @type: string
    """

    log = None
    """ 
    @ivar: This is the log object for the current class. 
    @type: logging
    """

    oConMgr = None
    """ 
    @ivar: This is the Connector Manager object
    @type: CNBConnectorManager
    """

    oConsole = None
    """ 
    @ivar: This is the Console object
    @type: CNBConsole
    """

    oMatrix = None
    """ 
    @ivar: This is the Matrix object
    @type: CNBMatrix
    """

    def __init__(self):
        Thread.__init__(self)
        oConfig = CNBConfig.getInstance()
        if oConfig.get('global', 'daemon'):
            self._bEnableShellConsole = False
        self.log = logging.getLogger(self.__class__.__name__)
        self._configLogs(oConfig)

        oMgr = CNBManager.getInstance()
        oMgr.setCNB(self)

        self.oConMgr = CNBConnectorManager()
        self.oConMgr.loadDefault()

        if self._bEnableShellConsole:
            self.oConsole = CNBConsole()
            self.oConsole.start()

        oMatrix = CNBMatrix.getInstance()

    def __del__(self):
        pass
    
    def _shutdown(self):
        """
        This method is called when the console is killed.
        """
        self.log.info('Going down')
    
    def _start(self):
        """
        This method is called when the bot is started
        """
        self.log.info('Starting all connections')
        self.oConMgr.startAll()

    def _stop(self):
        """
        This method is called when the bot is stopped
        """
        self.log.info('Stopping all connections')
        self.oConMgr.stopAll()

    def _die(self):
        """
        This method is called when the bot is killed
        """
        self.log.info('Killing Connector Manager')
        #del oConMgr
        self.oConMgr.killAll()
        
        #self.log.info('Killing Session Manager')
        #oSesMgr.kill()

        self.log.info('Killing Matrix')
        oMatrix = CNBMatrix.getInstance()
        #del oMatrix
        oMatrix.freeMM()

        self.log.info('Killing Console')
        #del oConsole
        self.oConsole.killConsole()
         
    def _configLogs(self, gConfig):
        """
        This method configure the logs for this object. 

        Two handlers are used, one to print to stdout and one to log in a file. For file, TimedRotatingFileHandler is used to rotate the log file every day. 

        @param gConfig: The gConfig object (the one that imported conf/cnb.conf).
        @type gConfig: CNBConfig
        """
        # Print output if not in daemon mode
        if not gConfig.get('global', 'daemon'):
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(gConfig.get('global', 'log-format')))
            self.log.addHandler(ch)

        # Write also to file
        fh = TimedRotatingFileHandler(\
            os.path.join(gConfig.get('global', 'log-dir'), 'cnb.log'), \
            backupCount=0, \
            when='d', \
            interval=1)
        fh.setFormatter(logging.Formatter(gConfig.get('global', 'log-format')))
        self.log.addHandler(fh)
        
        self.log.setLevel(logging.INFO)

    def run(self):
        """ 
        This method is called when the thread is started and contains the main loop
        """
        self.log.info('Serving forever...')

        # Start
        self.setState('starting')

        # Loop 
        while self.isRunning():
            if self.getState() == 'starting':
                self._start()
                self.setState('running')

            if self.getState() == 'running':
                try:
                    pass
                except KeyboardInterrupt:
                    self.log.info('bot stopped by user request. shutting down.')
                    self._die()
                    break

            if self.getState() == 'stopping':
                self._stop()
                self.setState('stopped')

            if self.getState() == 'stopped':
                pass

            if self.getState() == 'dying':
                self._die()
                break

            sleep(1)
        
        # When loop is done, shutdown
        self._shutdown()
        return 0

    def getState(self):
        """
        This method return the current state of CNB
        """
        return self._bState

    def setState(self, state):
        """
        This method set the current state of CNB
        """
        self._bState = state

    def isRunning(self):
        """
        Determine if CNB is running
        """
        if (self._bState in ['starting','running','stopping','stopped','dying']):
            return True
        else:
            return False

    def startCNB(self):
        """
        Start CNB
        """
        self.setState('starting')

    def stopCNB(self):
        """
        Stop CNB
        """
        self.setState('stopping')

    def killCNB(self):
        """
        Kill CNB
        """
        self.setState('dying')

