#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Chuck Norris Bot - Message
'''

from optparse import OptionParser

class CNBMessage():
    """
    This is the message object. Every message sent through a room or directly, will be converted into this class so the modules can deal with standard format.
    """
    
    protocol = None
    """
    @ivar: The protocol of the connector that was used to send the message. Should be one of these: xmpp | xmpp-gtalk | irc
    @type= string
    """

    type = None
    """
    @ivar: Type of the message. In xmpp, Should be one of these: chat | groupchat | normal (seems to be normal only from ejabberd servers)
    @ivar: Type of the message. In irc, it should be one of these: pubmsg | privmsg | notice
    @type: string
    """

    text = None
    """
    @ivar: Content of the message
    @type: string
    """

    nick = None
    """
    @ivar: Nick of the sender
    @type: string
    """

    replyTo = None
    """
    @ivar: User / Room to reply to (if "replyToUserOnly" is not set to True in the module class)
    @type: string
    """

    username = None
    """
    @ivar: User name of the sender (does not contains the domain in xmpp)
    @type: string
    """

    domain = None
    """
    @ivar: Domain of the sender. For xmpp here are some examples: hackfest.ca, gmail.com. For irc, the server is used (ex: irc.freenode.net)
    @type: string
    """

    cmd = None
    """
    @ivar: Command name. This is initialized from the initCmd() method
    @type: string
    """

    args = []
    """
    @ivar: Command arguments. This is initialized from the initCmd() method
    @type: List
    """

    #
    # XMPP Only
    #
    props = {}
    """
    @ivar: [xmpp only] Properties of a message sent in XMPP
    @type: Dictionnary
    """

    jid = None
    """
    @ivar: [xmpp only] JID
    @type: Unknown
    """

    email = None
    """
    @ivar: [xmpp only] Email address of the sender
    @type: string
    """

    room = None
    """
    @ivar: [xmpp only] room name, if the message is coming from a room (empty otherwise)
    @type: string
    """

    presType = None
    """
    @ivar: [xmpp only] presence type. It should be one of these: subscribe | subscribed | unsubscribe | unsubscribed | error | available | unavailable | dnd | away
    @type: string
    """

    presShow = None
    """
    @ivar: [xmpp only] presence show. Can be any message provided by a user. 
    @type: string
    """

    presSubscription = None
    """
    @ivar: [xmpp only] presence subscription. It should be one of these: to | both | from | none
    @type: string
    """

    #
    # IRC Only
    #
    target = None
    """
    @ivar: [irc only] Target of the message
    @type: string
    """

    source = None
    """
    @ivar: [irc only] Message sender
    @type: string
    """

    def __init__(self):
        pass
    
    def __del__(self):
        pass

    def initCmd(self):
        """
        Generate the cmd and args properties from the text property
        """
        a = self.text.split(' ')
        if len(a) == 0:
            self.cmd = ''
            self.args = []
        elif len(a) == 1:
            self.cmd = a[0]
            self.args = []
        elif len(a) > 1:
            self.cmd = a[0]
            self.args = a[1::]

    def printMsg(self):
        """
        Print the message and all its properties
        """
        print '----- START OF MESSAGE PRINTING -----'
        for i in dir(self):
            if i not in ['__init__', '__del__', '__module__', '__doc__']:
                print "Msg: oMsg." + str(i) + " = " + str(getattr(self,i))
        print '----- END OF MESSAGE PRINTING -----'
            
    def getFullName(self):
        return str(self.username) + '@' + str(self.domain)

    def getSource(self):
        if self.protocol.startswith('xmpp'):
            if '/' in self.jid:
                return self.jid.split('/')[0]
            else:
                return self.jid
        elif self.protocol.startswith('irc'):
            return str(self.target) + '@' + str(self.domain)
        else:
            return ''

    def getFullSource(self):
        if self.protocol.startswith('xmpp'):
            return self.jid
        elif self.protocol.startswith('irc'):
            return str(self.target) + '@' + str(self.domain) + '/' + str(self.username)
        else:
            return ''

