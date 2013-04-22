#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Chuck Norris Bot Manager
'''

# System imports
from singleton import Singleton

@Singleton
class CNBManager():
    """
    This singleton is a high level manager for CNB. 
    @todo: Is this really a good way to manage real time bots?
    """
    
    _oCNB = None

    def __init__(self):
        pass
    
    def __del__(self):
        pass

    def setCNB(self,oCNB):
        """
        Set the CNB main object
        @param oCNB: CNB Object
        @type oCNB: CNB
        """
        self._oCNB = oCNB

    def killCNB(self):
        """
        Kill CNB
        """
        self._oCNB.killCNB()

    def stopCNB(self):
        """
        Stop CNB
        """
        self._oCNB.stopCNB()

    def startCNB(self):
        """
        Start CNB
        """
        self._oCNB.startCNB()

    def joinCNB(self,conId,chan):
        """
        Join a chan/room on a specific connector
        @param conId: Connector ID
        @type conId: int
        @param chan: chan/room to join
        @type chan: String
        """
        return self._oCNB.joinCNB(conId,chan)

    def inviteCNB(self,conId,users,chan):
        """
        Invite a list of users on a chan/room for a specific connector
        @param conId: Connector ID
        @type conId: int
        @param users: List of users to invite
        @type users: List
        @param chan: chan/room to join
        @type chan: String
        """
        return self._oCNB.inviteCNB(conId,users,chan)

    def sayCNB(self,conId,user,msg):
        """
        Make CNB say something
        @param conId: Connector ID
        @type conId: int
        @param user: Destination user for the message
        @type users: String
        @param msg: Message to send
        @type msg: String
        """
        return self._oCNB.sayCNB(conId,user,msg)

    def sendFileCNB(self,conId,user,f):
        """
        Make CNB send a file to a user
        @param conId: Connector ID
        @type conId: int
        @param user: Destination user
        @type users: String
        @param f: File to send
        @type f: String
        """
        return self._oCNB.sendFileCNB(conId,user,f)

    def getConfigCNB(self,conId):
        """
        This method return the config object of a specific connector
        @param conId: Connector ID
        @type conId: int
        """
        return self._oCNB.getConfigCNB(conId)

    def getConIdCNB(self,domain):
        """
        This method return a connector ID for a valid domain
        @param domain: Domain name to search connector ID
        @type domain: string
        """
        return self._oCNB.getConIdCNB(domain)


