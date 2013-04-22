#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This is the main class of CNB. 
'''

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from singleton import Singleton
from cnbCore import CNBCore
from cnbConfig import CNBConfig
from cnbManager import CNBManager
from cnbConnectorManager import CNBConnectorManager
from cnbSessionManager import CNBSessionManager
from cnbConsole import CNBConsole

class CNB(CNBCore):
    """
    Once this class is instanciated, connections are initiated, console is started and the Matrix powered on. 

    This class mainly contain config and high level functions to interact with the bot. Most of the "back-end" code is in CNBCore class.
    """

    _bEnableShellConsole = True
    """ 
    @ivar: This let you choose if you start the console or not (daemon mode should not need it) 
    @type: bool
    @todo: Make the console work
    """

    _bEnableInstanceConsole = False
    """ 
    @ivar: This enable the console from an instance (Ex: The bot would be manageable from IRC). 
    @note: Currently not working.
    @type: bool
    @todo: Make Proto Console work
    """

    _bAutoConnect = True
    """ 
    @ivar: This make Chuck auto connect to all instances when started. Note that this is can be overwritten by user at startup. 
    @type: bool
    """

    _bAutoReconnect = True
    """ 
    @ivar: This make the bot reconnect an instance if this one fail/drop/disconnect. 
    @type: bool
    """

    def __init__(self):
        CNBCore.__init__(self)

    def __del__(self):
        CNBCore.__del__(self)

    def joinCNB(self,conId,chan):
        """
        This method let you connect a specific instance to a chan/room. 
        @param conId: a connection ID (auto generated).
        @type conId: int
        @param chan: a chan or a room (ex: on irc = #something, on xmpp = something@xmpp.server.com)
        @type chan: string
        """
        return self.oConMgr.joinChan(conId,chan)

    def inviteCNB(self,conId,users,chan):
        """
        This method let you invite someone to a chan/room on a specific instance.
        @param conId: a connection ID (auto generated).
        @type conId: int
        @param users: a list of users to invite
        @type users: array
        @param chan: a chan or a room (ex: on irc = #something, on xmpp = something@xmpp.server.com)
        @type chan: string
        """
        return self.oConMgr.inviteChan(conId,users,chan)

    def sayCNB(self,conId,dest,msg):
        """
        This method let you say something to a specific destination.
        @param conId: a connection ID (auto generated).
        @type conId: int
        @param dest: a user, a chan or a room (irc = #chan, irc = user, xmpp = room@xmpp.server.com, xmpp = user@xmpp.server.com
        @type dest: string
        @param msg: a message to say
        @type msg: string
        """
        return self.oConMgr.sendMsg(conId,dest,msg)

    def sendFileCNB(self,conId,dest,f):
        """
        This method let you send a file to a specific destination
        @param conId: a connection ID (auto generated).
        @type conId: int
        @param dest: a user
        @type dest: string
        @param f: a file to send
        @type f: string
        """
        return self.oConMgr.sendFile(conId,dest,f)

    def getConfigCNB(self,conId):
        """
        This method let you resolve a config object from a connection ID.
        @param conId: a connection ID (auto generated).
        @type conId: int
        """
        return self.oConMgr.getConfigFromId(conId)

    def getConIdCNB(self,domain):
        """
        This method return a connector ID for a valid domain
        @param domain: Domain name to search connector ID
        @type domain: string
        """
        return self.oConMgr.getConIdFromDomain(domain)
