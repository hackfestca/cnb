#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Chuck Norris Bot IRC Connector
'''

# Import system packages
import os
import re
import sys
import warnings
from time import sleep,time

# Import other packages
from cnbCon import CNBCon
from cnbConfig import CNBConfig
from cnbMatrix import CNBMatrix
from cnbMessage import CNBMessage
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    try:
        from irclib import IRC
        from irclib import ServerConnectionError
        from irclib import nm_to_n
        from irclib import parse_channel_modes
        from ircbot import IRCDict
        from ircbot import Channel
        from ircbot import is_channel    
    except ImportError:
        print >> sys.stderr, """
        You need to install irclib 
        On Debian-based systems, install the python-irclib package.
        Also check for the dependency script: /usr/local/cnb/scripts/inst-dep.sh
        """
        sys.exit(-1)
        
class CNBIRCCon(CNBCon):
    """
    IRC Connector class
    """

    # Constants
    IRC_REPLY_SLEEP = 0.5
    IRC_PORT = 6667
    IRC_CHAT = 'privmsg'

    _nickname = None
    """ 
    @ivar: Nick name of the bot
    @type: String
    """

    _realname = None
    """ 
    @ivar: Real Name of the bot
    @type: String
    """

    _password = None
    """ 
    @ivar: Bot password for identifying
    @type: String
    """

    server_list = []
    """ 
    @ivar: List of servers to connect
    @type: List
    """

    channels = {}
    """ 
    @ivar: List of joined channels
    @type: hashtable
    """

    channelsToJoin = []
    """ 
    @ivar: List of channels to join when the connector start
    @type: List
    """

    autoReconnect = False
    """ 
    @ivar: Determine if the bot will auto-reconnect if it disconnect/fail
    @type: bool
    """

    reconInterval = 60
    """ 
    @ivar: Reconnection interval (in sec)
    @type: int
    """

    connection = None
    """ 
    @ivar: Connection Object provided by irclib
    @type: Object
    """

    ircobj = None
    """ 
    @ivar: IRC Object provided by irclib
    @type: Object
    """

    def __init__(self, botConfig):
        CNBCon.__init__(self, botConfig)
        config = CNBConfig.getInstance()

        username = botConfig.get('bot', 'username')
        nickname = username
        realname = username
        channels = botConfig.get('bot', 'channels')
        password = botConfig.get('bot', 'password')
        server = botConfig.get('bot', 'server')
        autostart = botConfig.get('bot', 'auto-start')
        autoreconnect = botConfig.get('bot', 'auto-reconnect')
        reconInterval = 60

        self.ircobj = IRC()
        self.connection = self.ircobj.server()
        self.dcc_connections = []
        self.ircobj.add_global_handler("all_events", self._dispatcher, -10)
        #self.ircobj.add_global_handler("dcc_disconnect", self._dcc_disconnect, -10)

        self.autoReconnect = autoreconnect
        self.server_list.append([server, self.IRC_PORT])
        self.channelsToJoin = channels

        self.channels = IRCDict()
        if not reconInterval or reconInterval < 0:
            reconInterval = 2**31
        self.reconInterval = reconInterval

        self._nickname = nickname
        self._realname = realname
        self._password = password

        if autostart == '1':
            self.log.info('Auto-start = 1')
            self.startBot()

        if autoreconnect == '1':
            self.log.info('Auto-reconnect = 1')

    def __del__(self):
        pass

    def _shutdown(self):
        self.log.info('Going down')

    def _getMsgFromEvent(self, e, et = 'Msg'):
        """
        Generate a message object from an event
        @param e: Event
        @type e: Event
        @param et: 
        @type et: String
        """
        oMsg = CNBMessage()
        oMsg.protocol = 'irc'
        oMsg.conId = self._botConfig.get('bot', 'id')
        oMsg.type = str(e.eventtype())
        oMsg.isPrivate = (oMsg.type == 'privmsg' or oMsg.type == 'privnotice' or oMsg.type == 'invite')
        oMsg.source = str(e.source())
        oMsg.target = str(e.target())
        oMsg.text = str(e.arguments()[0]).strip()
        oMsg.domain = self._botConfig.get('bot', 'server')
        oMsg.initCmd()

        if oMsg.isPrivate:
            oMsg.username = str(e.source()).split('!')[0]
            oMsg.replyTo = str(e.source()).split('!')[0]
            if oMsg.type == 'invite':
                oMsg.room = oMsg.text
        else:
            #oMsg.username = str(e.target())
            oMsg.username = str(e.source()).split('!')[0]
            oMsg.replyTo = str(e.target())
            oMsg.room = str(e.target())

        # Logging
        for i in dir(oMsg):
            if i not in ['__init__', '__del__', '__module__', '__doc__']:
                self.log.debug(et + ": oMsg." + str(i) + " = " + str(getattr(oMsg,i)))
        
        return oMsg

    def _dispatcher(self, c, e):
        """[Internal]"""
        m = "_on_" + e.eventtype()
        if hasattr(self, m):
            getattr(self, m)(c, e)

    def _dcc_connect(self, address, port, dcctype="chat"):
        """
        Connect to a DCC peer.
        @param address: IP address of the peer.
        @param port: Port to connect to.
        @return: a DCCConnection instance.
        """
        dcc = self.ircobj.dcc(dcctype)
        self.dcc_connections.append(dcc)
        dcc.connect(address, port)
        return dcc

    def _dcc_listen(self, dcctype="chat"):
        """Listen for connections from a DCC peer.

        Returns a DCCConnection instance.
        """
        dcc = self.ircobj.dcc(dcctype)
        self.dcc_connections.append(dcc)
        dcc.listen()
        return dcc

    def _dcc_disconnect(self, c, e):
        """[Internal]"""
        self.dcc_connections.remove(c)
    
    def _connected_checker(self):
        """[Internal]"""
        if not self.connection.is_connected():
            self.log.info('Not connected, reconnecting')
            self.connection.execute_delayed(self.reconInterval,
                                            self._connected_checker)
            if self.autoReconnect:
                self._connect()

    def _connect(self):
        """[Internal]"""
        password = None
        if len(self.server_list[0]) > 2:
            password = self.server_list[0][2]
        try:
            self.log.info('Connecting to ' + self.server_list[0][0] + ':' + str(self.server_list[0][1]) + ' as ' + self._nickname + ' (ircname:' + self._realname + ')')
            self.connect(self.server_list[0][0],
                         self.server_list[0][1],
                         self._nickname,
                         password,
                         ircname=self._realname)
        except ServerConnectionError:
            self.log.info('Could not connect')

    def _disconnect(self, msg="I'll be back!"):
        """
        Disconnect the bot.
        The bot will try to reconnect after a while.
        @param msg: Quit message.
        @type msg: String
        """
        self.connection.disconnect(msg)

    def _on_ping(self, c, e):
        """[Internal]"""
        #self.log.debug('Received a ping, sending a pong')
        self.connection.pong(e.target())

    def _on_pubmsg(self, c, e):
        """[Internal]"""
        oMatrix = CNBMatrix.getInstance()
        oMsg = self._getMsgFromEvent(e, 'Pub Msg')
        if self._botConfig.get('bot', 'username') != oMsg.replyTo:
            replies = oMatrix.processIrcMod(oMsg)
            if replies != None:
                for r in replies:
                    c.privmsg(oMsg.replyTo, r)
                    sleep(self.IRC_REPLY_SLEEP)

    def _on_privmsg(self, c, e):
        """[Internal]"""
        oMatrix = CNBMatrix.getInstance()
        oMsg = self._getMsgFromEvent(e, 'Priv Msg')
        if self._botConfig.get('bot', 'username') != oMsg.replyTo:
            replies = oMatrix.processIrcMod(oMsg)
            if replies != None:
                for r in replies:
                    c.privmsg(oMsg.replyTo, r)
                    sleep(self.IRC_REPLY_SLEEP)
    
    def _on_pubnotice(self, c, e):
        """
        Pub Notice event handler
        Note: the bot do not answer to pub notice
        """
        oMsg = self._getMsgFromEvent(e, 'Pub Notice')

    def _on_privnotice(self, c, e):
        """[Internal]"""
        oMsg = self._getMsgFromEvent(e, 'Priv Notice')
        if oMsg.replyTo == 'NickServ' and 'You are now identified for' in oMsg.text:
            self.setState('identified')

    def _on_invite(self, c, e):
        """[Internal]"""
        oMatrix = CNBMatrix.getInstance()
        oMsg = self._getMsgFromEvent(e, 'Invite')
        if self._botConfig.get('bot', 'username') != oMsg.replyTo:
            replies = oMatrix.processIrcMod(oMsg)
            if replies != None:
                for r in replies:
                    c.privmsg(oMsg.replyTo, r)
                    sleep(self.IRC_REPLY_SLEEP)

    def _on_disconnect(self, c, e):
        """[Internal]"""
        self.channels = IRCDict()
        self.connection.execute_delayed(self.reconInterval,
                                        self._connected_checker)

    def _on_all_raw_messages(self, c, e):
        """[Internal]"""
        self.log.debug('Raw Message: ' + str(e.arguments()))

    def _on_error(self, c, e):
        """[Internal]"""
        self.log.info('Error: ' + str(c) + str(e))
        self.log.exception(str(c))
        self.log.exception(str(e))

    def _on_join(self, c, e):
        """[Internal]"""
        ch = e.target()
        nick = nm_to_n(e.source())
        self.log.info(nick + ' is joining channel ' + ch)
        if nick == c.get_nickname():
            self.channels[ch] = Channel()
        self.channels[ch].add_user(nick)

    def _on_kick(self, c, e):
        """[Internal]"""
        nick = e.arguments()[0]
        ch = e.target()

        self.log.info(nick + ' was kicked from ' + ch)
        if nick == c.get_nickname():
            del self.channels[ch]
        else:
            self.channels[ch].remove_user(nick)

    def _on_mode(self, c, e):
        """[Internal]"""
        modes = parse_channel_modes(" ".join(e.arguments()))
        t = e.target()
        self.log.info(t + ' set mode to ' + t)
        if is_channel(t):
            ch = self.channels[t]
            for mode in modes:
                if mode[0] == "+":
                    f = ch.set_mode
                else:
                    f = ch.clear_mode
                f(mode[1], mode[2])
        else:
            # Mode on self... XXX
            pass

    def _on_namreply(self, c, e):
        """
        [Internal]
        e.arguments()[0] == "@" for secret channels,
                             "*" for private channels,
                             "=" for others (public channels)
        e.arguments()[1] == channel
        e.arguments()[2] == nick list
        """

        ch = e.arguments()[1]
        for nick in e.arguments()[2].split():
            if nick[0] == "@":
                nick = nick[1:]
                self.channels[ch].set_mode("o", nick)
            elif nick[0] == "+":
                nick = nick[1:]
                self.channels[ch].set_mode("v", nick)
            self.channels[ch].add_user(nick)

    def _on_nick(self, c, e):
        """[Internal]"""
        before = nm_to_n(e.source())
        after = e.target()
        self.log.info(before + ' set nick to ' + after)
        for ch in self.channels.values():
            if ch.has_user(before):
                ch.change_nick(before, after)

    def _on_part(self, c, e):
        """[Internal]"""
        nick = nm_to_n(e.source())
        channel = e.target()
        self.log.info(nick + ' left the chan ' + channel)
        if nick == c.get_nickname():
            del self.channels[channel]
        else:
            self.channels[channel].remove_user(nick)

    def _on_quit(self, c, e):
        """[Internal]"""
        nick = nm_to_n(e.source())
        self.log.info(nick + ' has quit')
        for ch in self.channels.values():
            if ch.has_user(nick):
                ch.remove_user(nick)

    def _on_ctcp(self, c, e):
        """Default handler for ctcp events.

        Replies to VERSION and PING requests and relays DCC requests
        to the on_dccchat method.
        """
        if e.arguments()[0] == "VERSION":
            c.ctcp_reply(nm_to_n(e.source()),
                         "VERSION " + self.get_version())
        elif e.arguments()[0] == "PING":
            if len(e.arguments()) > 1:
                c.ctcp_reply(nm_to_n(e.source()),
                             "PING " + e.arguments()[1])
        elif e.arguments()[0] == "DCC" and e.arguments()[1].split(" ", 1)[0] == "CHAT":
            self.on_dccchat(c, e)

    def _on_dccchat(self, c, e):
        """[Internal]"""
        pass

    def run(self):
        """
        IRC connector main thread - Listen to commands, parse messages and responses to users.
        """
        while self.isRunning():
            if self.getState() == 'dying':
                break

            if self.getState() in ['connected', 'identifying', 'joiningChannels']:
                try:
                    self.ircobj.process_once(1)
                except KeyboardInterrupt:
                    self.log.info('bot stopped by user request. shutting down.')
                    break
                except Exception, e:
                    self.log.exception(e)

            if self.getState() == 'joiningChannels':
                for ch in self.channelsToJoin:
                    if ':' in ch:
                        ch,pwd = ch.split(':',1)
                        self.joinChan(ch,pwd)
                    else:
                        self.joinChan(ch)
                self.setState('connected')

            if self.getState() == 'identified':
                self.log.info('Identified, joining channels...')
                self.setState('joiningChannels')
                #sleep(2)
                self.ircobj.process_once(0.5)

            if self.getState() == 'identifying':
                if self._password:
                    self.log.info('Identifying with password')
                    self.identify(self._password)
                    #sleep(2)
                    self.ircobj.process_once(0.5)
                self.setState('identified')

            if self.getState() == 'connecting':
                self._connect()
                if self.connection.is_connected():
                    self.log.info('bot connected, identifying...')
                    self.setState('identifying')
                    sleep(5)
                    self.ircobj.process_once(0.5)
                else:
                    self.log.warn('could not connect to server - aborting.')
                    self.setState('disconnected')

            if self.getState() == 'disconnected':
                #self.log.info('bot disconnected')
                if self.autoReconnect:
                    self.setState('connecting')
                    self.ircobj.process_once(0.5)

            if self.getState() == 'disconnecting':
                self.log.info('bot disconnecting')
                self._disconnect()
                self.setState('disconnected')

            if self.getState() == 'notstarted':
                pass

           # self.log.info('Current state: ' + self.getState())
            sleep(1)

        self._shutdown()
        return 0

    def connect(self, server, port, nickname, password=None, username=None,
                ircname=None, localaddress="", localport=0, ssl=False, ipv6=False):
        """
        Connect/reconnect to a server.

        @param server: Server name.
        @param port: Port number.
        @param nickname: The nickname.
        @param password: Password (if any).
        @param username: The username.
        @param ircname: The IRC name.
        @param localaddress: Bind the connection to a specific local IP address.
        @param localport: Bind the connection to a specific local port.
        @param ssl: Enable support for ssl.
        @param ipv6: Enable support for ipv6.
        """
        self.connection.connect(server, port, nickname,
                                password, username, ircname,
                                localaddress, localport, ssl, ipv6)

    def get_version(self):
        """
        Returns the bot version.
        Used when answering a CTCP VERSION request.
        """
        return "CNB Project by Martin <martin.dube@gmail.com>, based on ircbot.py by Joel Rosdahl <joel@rosdahl.net>"

    def jump_server(self, msg="Changing servers"):
        """
        Connect to a new server, possibly disconnecting from the current.

        The bot will skip to next server in the server_list each time
        jump_server is called.
        """
        if self.connection.is_connected():
            self.connection.disconnect(msg)
        self.log.info('Jumping server')
        self.server_list.append(self.server_list.pop(0))
        self._connect()

    def identify(self, password):
        """
        Identify command (Freenode)
        @param password: Password sent to identify the user
        @type password: String
        """
        self.connection.privmsg('NickServ', ' identify ' + password)

    def joinChan(self,chan,pwd = None):
        """
        This method let the bot join a channel
        @param chan: Channel name
        @type chan: String
        @param pwd: Channel password if any
        @type pwd: String
        """
        self.log.info('Joining channel: ' + chan)
        if pwd:
            self.connection.join(chan,pwd)
        else:
            self.connection.join(chan)

    def sendMsg(self,user,msg):
        """
        This method send a message to a user or a chan
        @param user: User or chan to send a message
        @type user: String
        @param msg: Message to send
        @type msg: String
        """
        self.log.info('Sending message to: ' + user)
        aMsg = msg.split("\n")
        for m in aMsg:
            self.connection.privmsg(user, m)
            sleep(self.IRC_REPLY_SLEEP)

    def isValidDomain(self, domain):
        """
        Determine if a domain is valid for this connection (Ex: for xmpp, there are muc domains (gmail.com) and user domains (talk.google.com))
        @param domain: The domain to check
        @type domain: string
        """
        if domain == self._botConfig.get('bot', 'server'):
            return True
        else:
            return False

