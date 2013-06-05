#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This is the Connector Manager class of CNB
'''

# System imports
import os
import logging
from ConfigParser import RawConfigParser
from logging.handlers import TimedRotatingFileHandler
from cnbXmppCon import CNBXMPPCon
from cnbIrcCon import CNBIRCCon
from cnbConfig import CNBConfig

class CNBConnectorManager():
    """
    This class manage the connectors (xmpp, irc, sip, etc.). This class let you start instances, stop instances, load from file, join room/chan, invite people to room/chan, etc.
    """

    _aConList = []
    """
    @ivar: This var contains the list of connector object
    @type: list
    """

    _nextId = 0
    """
    @ivar: This is the incremental index of the connectors
    @type: int
    """

    log = None
    """
    @ivar: This is the log object of CNBConnectorManager
    @type: logging
    """

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self._configLogs()

    def __del__(self):
        self.killAll()

    def _getConFromId(self, conId):
        """
        Return a connector object from an ID
        @param conId: a connection ID (auto generated).
        @type conId: int
        """
        for c in self._aConList:
            if str(c.getConfig().get('bot', 'id')) == str(conId):
                return c
        return None

    def _configLogs(self):
        """
        This method configure the logs for this object. 

        Two handlers are used, one to print to stdout and one to log in a file. For file, TimedRotatingFileHandler is used to rotate the log file every day. 
        """
        config = CNBConfig.getInstance()

        # Print output if not in daemon mode
        if not config.get('global', 'daemon'):
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(config.get('global', 'log-format')))
            self.log.addHandler(ch)

        # Write also to file
        fh = TimedRotatingFileHandler(\
            os.path.join(config.get('global', 'log-dir'), 'cnb-conmanager.log'), \
            backupCount=0, \
            when='d', \
            interval=1)
        fh.setFormatter(logging.Formatter(config.get('global', 'log-format')))
        self.log.addHandler(fh)
        
        self.log.setLevel(logging.INFO)

    def _normalize(self,c):
        """
        This method let you import arrays from config files. The syntax must be: "var: ['value1','value2','...']". 
        @param c: Config object to parse.
        @type c: Config object
        """
        for s in c.sections():
            for (n,v) in c.items(s):
                if n not in ['password']:
                    self.log.info('Var: ' + n + ' = ' + v)
                if (len(v) > 0):
                    if v[0] == '[' and v[len(v)-1] == ']':
                        nv = self._striplist((v[1:-1]).split(','))
                    else:
                        nv = v.strip()
                    c.set(s,n,nv)
                else:
                    c.set(s,n,v)
        return c

    def _striplist(self,l):
        """
        This method strip a list of strings
        @param l: List to parse
        @type l: List
        """
        return([x.strip() for x in l])

    def loadDefault(self):
        """
        This method load the default connectors from the "cnb.conf" file.
        """
        config = CNBConfig.getInstance()
        aList = config.get('connectors', 'auto')
        sConfigFolder = config.get('global', 'config-dir')
        if sConfigFolder[len(sConfigFolder)-1] != '/':
            sConfigFolder = sConfigFolder + '/'
        for s in aList:
            oCon = self.loadFromFile(sConfigFolder + s)
            if oCon:
                self.log.info('Appending oCon.id = ' + str(oCon.getConfig().get('bot', 'id')))
                self._aConList.append(oCon)

    def loadFromFile(self,sFile):
        """
        This method load a Connector object from a file
        @param sFile: File containing the connector configuration (Ex: conf/name.type.conf)
        @type sFile: String
        """
        config = CNBConfig.getInstance()
        self.log.info('Loading instance: "' + sFile + '"')
        botConfig = RawConfigParser()
        try:
            botConfig.readfp(open(sFile))
            botConfig = self._normalize(botConfig)
        except Exception, e:
            self.log.error('Could not open config file: ' + sFile)
            self.log.exception(e)
            botConfig = None
            return None
       
        botConfig.set('bot', 'config-file', sFile)
        botConfig.set('bot', 'id', self._nextId)
        self._nextId = self._nextId + 1

        if botConfig.get('bot', 'type').startswith('xmpp'):
            bot = CNBXMPPCon(botConfig)
        elif botConfig.get('bot', 'type') == 'irc':
            bot = CNBIRCCon(botConfig)

        bot.start()

        return bot

    def killConFromId(self, conId):
        """
        Kill a connector from an ID
        @param conId: Connector ID
        @type conId: int
        """
        self.log.info('Killing connection: ' + str(conId))
        c = self._getConFromId(conId)
        c.killBot()

    def killAll(self):
        """
        Kill all active connectors
        """
        self.log.info('Killing all connection')
        for c in self._aConList:
            if(c and c.getConfig()):
                self.log.info('Killing: ' + str(c.getConfig().get('bot', 'id')))
                c.killBot()

    def stopConFromId(self, conId):
        """
        Stop a connector from an ID
        @param conId: Connector ID
        @type conId: int
        """
        self.log.info('Stopping connection: ' + str(conId))
        c = self._getConFromId(conId)
        c.stopBot()

    def stopAll(self):
        """
        Stop all active connectors
        """
        self.log.info('Stopping all connection')
        for c in self._aConList:
            if(c and c.getConfig()):
                self.log.info('Stopping: ' + str(c.getConfig().get('bot', 'id')))
                c.stopBot()

    def startConFromId(self, conId):
        """
        Start a connector from an ID
        @param conId: Connector ID
        @type conId: int
        """
        self.log.info('Starting connection: ' + str(conId))
        c = self._getConFromId(conId)
        c.startBot()

    def startAll(self):
        """
        Start all stopped connectors
        """
        self.log.info('Starting all connection')
        for c in self._aConList:
            if(c and c.getConfig()):
                self.log.info('Starting: ' + str(c.getConfig().get('bot', 'id')))
                c.startBot()

    def joinChan(self,conId,chan):
        """
        Join a chan/room for a specific connection
        @param conId: Connector ID
        @type conId: int
        @param chan: Name of the channel (irc) or room (xmpp) to join
        @type chan: string
        """
        self.log.info('Joining a chan/room')
        c = self._getConFromId(conId)
        protocol = c.getConfig().get('bot', 'type')
        if protocol.startswith('xmpp'):
            c.joinRoom(chan)
        if protocol == 'irc':
            c.joinChan(chan)

        return ''

    def inviteChan(self,conId,users,chan):
        """
        Invite a list of people on a chan/room for a specific connection
        @param conId: Connector ID
        @type conId: int
        @param chan: Name of the channel (irc) or room (xmpp) to join
        @type chan: string
        """
        self.log.info('Inviting people to a chan/room')
        c = self._getConFromId(conId)
        protocol = c.getConfig().get('bot', 'type')
        if protocol.startswith('xmpp'):
            c.inviteToRoom(users,chan)
        if protocol == 'irc':
            #
            pass

        return ''

    def sendMsg(self,conId,dest,msg):
        """
        Send a message to a user/room for a specific connection
        @param conId: Connector ID
        @type conId: int
        @param dest: Name of the channel (irc), room (xmpp) or user send a message 
        @type dest: string
        @param msg: Message to send
        @type msg: string
        """
        self.log.info('Writting a msg to: ' + dest)
        c = self._getConFromId(conId)
        protocol = c.getConfig().get('bot', 'type')
        if protocol.startswith('xmpp'):
            c.send(dest, msg)
            c.send(dest, msg,None,'groupchat')
        if protocol == 'irc':
            c.sendMsg(dest,msg)

        return ''

    def sendFile(self,conId,dest,f):
        """
        Send a file to a user for a specific connection
        @param conId: Connector ID
        @type conId: int
        @param dest: Name of user send a message 
        @type dest: string
        @param f: File to send
        @type f: string
        """
        self.log.info('Sending a file to: ' + dest)
        c = self._getConFromId(conId)
        protocol = c.getConfig().get('bot', 'type')
        if protocol.startswith('xmpp'):
            c.sendFile(dest, f)

        return ''

    def getConfigFromId(self,conId):
        """
        Get a config object from a connector ID
        @param conId: Connector ID
        @type conId: int
        """
        return self._getConFromId(conId).getConfig()

    def getConIdFromDomain(self,domain):
        """
        This method return a connector ID for a valid domain
        @param domain: Domain name to search connector ID
        @type domain: string
        """
        for c in self._aConList:
            if c.isValidDomain(domain):
                return c.getConfig().get('bot', 'id')
        return None
