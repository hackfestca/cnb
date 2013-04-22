#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab tabstop=4 shiftwidth=4 softtabstop=4

'''
Chuck Norris Bot - XMPP Connector
'''

# Import system packages
import os
import re
import sys
import uuid
import warnings
import StringIO
from time import sleep,time

# Import other packages
from cnbCon import CNBCon
from cnbConfig import CNBConfig
from cnbMatrix import CNBMatrix
from cnbMessage import CNBMessage
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    try:
        import xmpp
    except ImportError:
        print >> sys.stderr, """
        You need to install xmpppy from http://xmpppy.sf.net/.
        On Debian-based systems, install the python-xmpp package.
        Also check for the dependency script: /usr/local/cnb/scripts/inst-dep.sh
        """
        sys.exit(-1)

    try:
        from django.utils.encoding import smart_str
    except ImportError:
        print >> sys.stderr, """
        You need to install django.
        On Debian-based systems, install the python-django package.
        Also check for the dependency script: /usr/local/cnb/scripts/inst-dep.sh
        """
        sys.exit(-1)

class CNBXMPPCon(CNBCon):
    """
    This class manage every communication with a xmpp server using xmpp python library
    @note: The protocol is not exactly the same between gmail and a custom xmpp server (tested with ejabberd). 
    """

    # Constants
    #GMAIL_USER_DOMAIN = 'gmail.com'
    #HF_USER_DOMAIN = 'hackfest.ca'
    #GMAIL_MUC_DOMAIN = 'talk.google.com'
    #HF_MUC_DOMAIN = 'conference.hackfest.ca'
    AVAILABLE, AWAY, CHAT, DND, XA, OFFLINE = None, 'away', 'chat', 'dnd', 'xa', 'unavailable'
    MSG_AUTHORIZE_ME = 'Hey there. You are not yet on my roster. Authorize my request and I will do the same.'
    MSG_NOT_AUTHORIZED = 'You did not authorize my subscription request. Access denied.'
    MSG_UNKNOWN_COMMAND = 'Unknown command: "%(command)s". Type ".help" for available commands.'
    XMPP_CHAT, XMPP_GROUPCHAT = 'chat', 'groupchat'
    PING_FREQUENCY = 30 # Set to the number of seconds, e.g. 60.
    PING_TIMEOUT = 10 # Seconds to wait for a response.
    MAX_REPLY_SIZE = 10000
    SLEEP_TIME_BETWEEN_REPLY = 1    # https://developers.google.com/appengine/docs/java/xmpp/overview?hl=us#Quotas_and_Limits

    _joinedRooms = []
    """
    @ivar: list of joined chat rooms
    @type: List
    """

    _username = ''
    """
    @ivar: Username of the current account
    @type: string
    """

    _password = ''
    """
    @ivar: Password of the current account
    @type: string
    """

    _privatedomain = False
    """
    @ivar: Specify a private domain. Useful if the domain can't be resolved from the DNS (ex: _client-xmpp._tcp.domain.com)
    @type: string
    """

    _acceptownmsgs = False
    """
    @ivar: Accept own messages. False by default. Never tested with True (I guess it would be weird or just fuck the bot)
    @type: bool
    """

    _debug = False
    """
    @ivar: connect the bot in debug mode (xmpp python library feature)
    @type: bool
    """

    _show = None
    """
    @ivar: The "show" message (part of the status)
    @type: string
    """

    _status = None
    """
    @ivar: Status of the bot
    @type: string
    """

    _seen = {}
    """
    @ivar: Dictionnary of (show,status) for all seen users
    @type: dictionnary
    """

    _threads = {}
    """
    @ivar: Keep a list of threads (people the bot talk to) to facilitate reply
    @type: dictionnary
    """

    _lastping = time()
    """
    @ivar: Keep the last ping time
    @type: time
    """
    
    _rooms = []
    """
    @ivar: List of rooms to join to by default. They are defined in the config file.
    @type: List
    """

    _res = None
    """
    @ivar: Optionnal ressource name
    @type: string
    """

    jid = None
    """
    @ivar: JID of the current user
    @type: JID
    """

    contacts = {}
    """
    @ivar: Dictionnary of contacts (friends) for the current account
    @type: dictionnary
    """

    roster = None
    """
    @ivar: Contact list of the bot
    @type: Object
    @see: http://xmpp.org/rfcs/rfc3921.html#intro-requirements
    """

    conn = None
    """
    @ivar: Connection Handler
    @type: Object
    """

    ibb = None
    """
    @ivar: File Transfer Handler
    @type: Object
    """

    def __init__(self, botConfig):
        CNBCon.__init__(self, botConfig)
        config = CNBConfig.getInstance()

        self._username = botConfig.get('bot', 'username')
        self._password = botConfig.get('bot', 'password')
        server = botConfig.get('bot', 'server')
        self._rooms = botConfig.get('bot', 'rooms')
        self._autostart = botConfig.get('bot', 'auto-start')
        self.autoReconnect = botConfig.get('bot', 'auto-reconnect')
        self._res = self.__class__.__name__
        if server == '':
            #self.jid = xmpp.JID(self._username)
            self.log.info('Not server specified')
        else:
            #self.jid = xmpp.JID(self._username, server)
            self.log.info('Server specified: ' + server)

        if self._autostart == '1':
            self.log.info('Auto-start = 1')
            self.startBot()

        if self.autoReconnect == '1':
            self.log.info('Auto-reconnect = 1')

        # GTalk specificity
        if botConfig.get('bot','type') == 'xmpp-gtalk':
            self._initMondaySuckRoom()
    
    def __del__(self):
        pass

    def _initMondaySuckRoom(self):
        """
        Initialize the "Monday suck" room. This method is called when the class is initialize but can also be called to reset room when the ownership is lost (gmail)
        """
        sGTalkDefaultRoom = 'private-chat-' + str(uuid.uuid1()) + '@groupchat.google.com'
        self._botConfig.set('bot', 'monday-suck-room', sGTalkDefaultRoom)

    def _callback_message(self, conn, mess):
        """
        Changes the behaviour of the JabberBot in order to allow it to answer direct messages. 
        This is used often when it is connected in MUCs (multiple users chatroom). 

        @param conn: Connection handle
        @type conn: Object
        @param mess: Message sent to the bot
        @type mess: Object
        """
        self._lastping = time()
        reply = None

        oMsg = CNBMessage()
        oMsg.protocol = self._botConfig.get('bot', 'type')
        oMsg.conId = self._botConfig.get('bot', 'id')
        oMsg.type = str(mess.getType())
        oMsg.isPrivate = (oMsg.type == self.XMPP_CHAT)
        oMsg.jid = str(mess.getFrom())
        oMsg.error = mess.getError()
        oMsg.nick = mess.getFrom().getResource()
        oMsg.props = mess.getProperties()
        oMsg.email = mess.getFrom().getStripped()
        oMsg.username = self.get_sender_username(mess)
        if len(oMsg.email.split('@')) > 1:
            oMsg.domain = oMsg.email.split('@')[1]
        oMsg.text = smart_str(mess.getBody()).strip()
        oMsg.initCmd()

        if '/' in oMsg.jid:
            oMsg.room = oMsg.jid.split('/')[0]
        else:
            oMsg.room = oMsg.jid

        if oMsg.type == self.XMPP_CHAT:
            oMsg.replyTo = oMsg.username
        else:
            oMsg.replyTo = oMsg.room

        if ' ' in oMsg.text:
            command, args = oMsg.text.split(' ', 1)
        else:
            command, args = oMsg.text, ''
        oMsg.cmd = command.lower()

        # Logging
        for i in dir(oMsg):
            if i not in ['__init__', '__del__', '__module__', '__doc__']:
                self.log.debug("Msg: oMsg." + str(i) + " = " + str(getattr(oMsg,i)))

        if oMsg.type not in ("groupchat", "chat", "normal"):
            self.log.debug("unhandled message type: %s" % type)
            return

        # Ignore messages from before we joined
        if xmpp.NS_DELAY in oMsg.props: return

        # Ignore messages from myself
        if self.jid.bareMatch(oMsg.jid): return

        # Logging message
        # Not logging because it is already logged in cnb-matrix.log
        #self.log.info("%s> %s" % (oMsg.jid, oMsg.text))
        #self.log.debug("*** cmd = %s" % oMsg.cmd)

        # If a message format is not supported (eg. encrypted), txt will be None
        if not oMsg.text: return

        # Ignore messages from users not seen by this bot
        #if jid not in self._seen:
        #    self.log.info('Ignoring message from unseen guest: %s' % jid)
        #    self.log.debug("I've seen: %s" % ["%s" % x for x in self._seen.keys()])
        #    return

        # Remember the last-talked-in thread for replies
        self._threads[oMsg.jid] = mess.getThread()

        # In private chat, it's okay for the bot to always respond.
        # In group chat, the bot should silently ignore commands it
        # doesn't understand or aren't handled by _unknown_command().
        if oMsg.type == 'groupchat':
            default_reply = None
        else:
            default_reply = self.MSG_UNKNOWN_COMMAND % {'command': oMsg.cmd}
            reply = self._unknown_command(mess, oMsg.cmd, args)
            
        # Else
        if reply is None:
            reply = default_reply
        else:
            self.send_simple_reply(mess, reply)

        # Process Response if text is not null and sender is not the bot
        if oMsg.text != '' \
           and oMsg.text != 'None' \
           and oMsg.username != self._botConfig.get('bot', 'username').split('@')[0]:
            oMatrix = CNBMatrix.getInstance()
            reply = oMatrix.processXmppMod(oMsg)
            
            # if reply is too big, split into smaller block
            if reply and len(reply) > self.MAX_REPLY_SIZE:
                aReplies = self._splitByLine(reply,self.MAX_REPLY_SIZE)
                self.log.debug('Splitted the reply in ' + str(len(aReplies)) + ' blocks of ' + str(self.MAX_REPLY_SIZE))
                for r in aReplies: 
                    self.send_simple_reply(mess, r)
                    sleep(self.SLEEP_TIME_BETWEEN_REPLY)
            elif reply:
                self.send_simple_reply(mess, reply)

    def _callback_presence(self, conn, presence):
        """
        Presence callback function. useful to trigger events based on presence
        @param conn: Connection handle
        @type conn: Object
        @param presence: Presence notification
        @type presence: Object
        """
        self._lastping = time()

        oMsg = CNBMessage()
        oMsg.protocol = self._botConfig.get('bot', 'type')
        oMsg.conId = self._botConfig.get('bot', 'id')
        oMsg.jid = str(presence.getFrom())
        oMsg.error = presence.getError()
        oMsg.presType = smart_str(presence.getType())
        oMsg.presShow = smart_str(presence.getShow())
        oMsg.presStatus = smart_str(presence.getStatus())

        if '/' in oMsg.jid:
            oMsg.room = oMsg.jid.split('/')[0]
        else:
            oMsg.room = oMsg.jid

        # Logging
        for i in dir(oMsg):
            if i not in ['__init__', '__del__', '__module__', '__doc__']:
                self.log.debug("Presence: oMsg." + str(i) + " = " + str(getattr(oMsg,i)))

        jid, type_, show, status = presence.getFrom(), \
            presence.getType(), presence.getShow(), \
            presence.getStatus()

        if self.jid.bareMatch(jid):
            # update internal status
            if type_ != self.OFFLINE:
               self._status = status
               self._show = show
            else:
               self._status = ""
               self._show = self.OFFLINE
            if not self._acceptownmsgs:
               # Ignore our own presence messages
               return

        if type_ is None:
            # Keep track of status message and type changes
            old_show, old_status = self._seen.get(jid, (self.OFFLINE, None))
            if old_show != show:
                self._status_type_changed(jid, show)

            if old_status != status:
                self._status_message_changed(jid, status)

            self._seen[jid] = (show, status)
        elif type_ == self.OFFLINE and jid in self._seen:
            # Notify of user offline status change
            del self._seen[jid]
            self._status_type_changed(jid, self.OFFLINE)

        try:
            subscription = self.roster.getSubscription(unicode(jid.__str__()))
        except KeyError, e:
            # User not on our roster
            subscription = None
        except AttributeError, e:
            # Recieved presence update before roster built
            return

        if type_ == 'error':
            self.log.error('[presence]' + presence.getError())

            if presence.getError() == 'not-allowed' \
                and self._botConfig.has_option('bot', 'monday-suck-room') \
                and oMsg.room == self._botConfig.get('bot', 'monday-suck-room'):
                self._initMondaySuckRoom()

        self.log.debug('Got presence: %s (type: %s, show: %s, status: %s, subscription: %s)' % (jid, type_, show, status, subscription))

        # If subscription is private, disregard anything not from the private domain
        if self._privatedomain and type_ in ('subscribe', 'subscribed', 'unsubscribe'):
            if self._privatedomain == True:
                # Use the bot's domain
                domain = self.jid.getDomain()
            else:
                # Use the specified domain
                domain = self._privatedomain

            # Check if the sender is in the private domain
            user_domain = jid.getDomain()
            if domain != user_domain:
                self.log.info('Ignoring subscribe request: %s does not match private domain (%s)' % (user_domain, domain))
                return

        if type_ == 'subscribe':
            # Incoming presence subscription request
            if subscription in ('to', 'both', 'from'):
                self.roster.Authorize(jid)
                self._send_status()

            if subscription not in ('to', 'both'):
                self.roster.Subscribe(jid)

            if subscription in (None, 'none'):
                self.send(jid, self.MSG_AUTHORIZE_ME)
        elif type_ == 'subscribed':
            # Authorize any pending requests for that JID
            self.roster.Authorize(jid)
        elif type_ == 'unsubscribed':
            # Authorization was not granted
            self.send(jid, self.MSG_NOT_AUTHORIZED)
            self.roster.Unauthorize(jid)

        # Process any module for stats or more
        if oMsg.presType in ['None', self.AVAILABLE, self.AWAY, self.CHAT, self.DND, self.XA, self.OFFLINE]:
            oMatrix = CNBMatrix.getInstance()
            oMatrix.processXmppMod(oMsg)

    def _callback_iq(self, conn, iq_node):
        """
        IQ callback function. A IQ query is a way to query a xmpp server for some informations (ex: get list of members in a room). 
        IQ Responses are handled here.
        @param conn: Connection handle
        @type conn: Object
        @param iq_node: IQ Node
        @type iq_node: Object
        """
        node = str(iq_node)

        #we've got an online users list
        if 'http://jabber.org/protocol/disco#items' in node:
            print 'IQ NODE: ' + node
            regex = re.compile(r'name="([\w.]+)"')
            matches = regex.finditer(node)
            self.online_users = []
            for m in matches:
                self.online_users.append(m.group(1))

        return

    def _status_type_changed(self, jid, new_status_type):
        """
        Callback for tracking status types (available, away, offline, ...)
        @param jid: JID of the user who changed status type
        @type jid: JID
        @param new_status_type: The new status type
        @type new_status_type: string
        """
        self.log.debug('user %s changed status to %s' % (jid, new_status_type))

    def _status_message_changed(self, jid, new_status_message):
        """
        Callback for tracking status messages (the free-form status text)
        @param jid: JID of the user who changed status message
        @type jid: JID
        @param new_status_message: The new status message
        @type new_status_message: string
        """
        self.log.debug('user %s updated text to %s' % (jid, new_status_message))

    def _unknown_command(self, mess, cmd, args):
        """Default handler for unknown commands

        Override this method in derived class if you
        want to trap some unrecognized commands.  If
        'cmd' is handled, you must return some non-false
        value, else some helpful text will be sent back
        to the sender.
        """
        return None

    def _send_status(self):
        """
        Send the bot status to the server
        """
        self.conn.send_status()

    def __get_status(self):
        """
        Get the bot status
        """
        return self._status

    # wtf?
    #status_message = property(fget=__get_status, fset=__set_status)

    def __set_show(self, value):
        """
        Set the bot show
        @param value: Name of the show
        @type value: string
        """
        if self._show != value:
            self._show = value
            self._send_status()

    def __get_show(self):
        """
        Get the bot show
        """
        return self._show

    #wtf?
    #status_type = property(fget=__get_show, fset=__set_show)
        
    def _shutdown(self):
        """
        This function will be called when the bot is done serving.
        """
        self.log.info('Going down')
    
    def _connect(self):
        """
        This method is called when the bot is ready to connect a xmpp server (called by "connecting" state).
        This part manage SASL, TLS and such things.
        """
        if not self.conn:
            if len(self._username.split('@')) > 1:
                nod = self._username.split('@')[0]
                dom = self._username.split('@')[1]
            else:
                nod = None
                dom = None
            if self._debug:
                conn = xmpp.Client(dom)
            else:
                conn = xmpp.Client(dom, debug=[])

            conres = conn.connect()
            if not conres:
                self.log.error('unable to connect to server %s.' % self.jid.getDomain())
                return None
            if conres != 'tls':
                self.log.warning('unable to establish secure connection - TLS failed!')

            authres = conn.auth(nod, self._password, self._res)
            if not authres:
                self.log.error('unable to authorize with server.')
                return None
            if authres != 'sasl':
                self.log.warning("unable to perform SASL auth os %s. Old authentication method used!" % self.jid.getDomain())

            conn.sendInitPresence()
            self.conn = conn
            self.updateRosters()
            self.conn.RegisterHandler('message', self._callback_message)
            self.conn.RegisterHandler('presence', self._callback_presence)
            self.conn.RegisterHandler('iq', self._callback_iq)

            # Set current JID
            self.jid = xmpp.JID(node=conn.User, domain=conn.Server, resource=conn.Resource)
            self.log.info('self.jid.getNode() = ' + self.jid.getNode())
            self.log.info('self.jid.getDomain() = ' + self.jid.getDomain())
            self.log.info('self.jid.getResource() = ' + self.jid.getResource())

            # Set File Transfer Handler
            #self.ibb = xmpp.filetransfer.IBB()
            #self.ibb.PlugIn(self.conn)
        return self.conn
    
    def _disconnect(self):
        """
        This method is called when the bot can disconnect.
        @note: This is not called when there's a timeout, otherwise it freeze.
        """ 
        if self.conn:
            self.conn.disconnect()
            self.conn = None

    def _idle_ping(self):
        """
        Pings the server, calls _on_ping_timeout() on no response.
        To enable set self.PING_FREQUENCY to a value higher than zero.
        """
        if self.PING_FREQUENCY and time() - self._lastping > self.PING_FREQUENCY:
            self._lastping = time()
            ping = xmpp.Protocol('iq', typ='get', payload=[xmpp.Node('ping', attrs={'xmlns':'urn:xmpp:ping'})])
            self.log.debug('Pinging the server: ' + str(ping))
            try:
                res = self.conn.SendAndWaitForResponse(ping, self.PING_TIMEOUT)
                self.log.debug('Got response: ' + str(res))
                if res is None:
                    self._on_ping_timeout()
            except IOError, e:
                self.log.error('Error pinging the server: %s, treating as ping timeout.' % e)
                self._on_ping_timeout()

    def _on_ping_timeout(self):
        """
        Timeout handler
        This function is called when timeout occur. Important: The _disconnect() function must not be called from here because it freeze.
        """
        self.log.info('Terminating due to PING timeout.')
        self.setState('disconnected')

    def _splitByLine(self,txt,maxl):
        """
        Split a string, with the \n delimiter, into blocks that are smaller than maxl.
        @param text: String to split
        @type text: string
        @param maxl: Max Length of the split
        @type maxl: int
        """
        aTxt = txt.split("\n")
        ret = ['']
        i = 0
        for l in aTxt:
            if len(l)+len(ret[i]) <= maxl:
                ret[i] = ret[i] + "\n" +  l
            elif len(l) > maxl:
                i = i + 1
                ret.append('')
            else:
                i = i + 1
                ret.append(l + "\n")
        return ret

    def run(self):
        """
        Bot main thread - Process xmpp messages and trigger the right events depending on the registered handlers
        """
        self._lastping = time()
        while self.isRunning():
            
            if self.getState() == 'dying':
                break

            if self.getState() == 'connected':
                try:
                    self.conn.Process(1)
                    self.idle_proc()
                except KeyboardInterrupt:
                    self.log.info('bot stopped by user request. shutting down.')
                    break
                except xmpp.protocol.SystemShutdown:
                    self.log.info('System was shutted down... disconnected')
                    self.setState('disconnected')
                # tmp
                except 'not-allowed':
                    self.log.info('[run] Not allowed')
                    self.log.exception(e)
                except IOError, e:
                    self.log.info('IOError: ' + str(e))
                    self.setState('disconnected')
                except Exception, e:
                    self.log.exception(e)

            if self.getState() == 'joiningRooms':
                for r in self._rooms:
                    self.joinRoom(r)
                self.setState('connected')

            if self.getState() == 'connecting':
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=DeprecationWarning)
                    self._connect()
                if self.conn:
                    self.log.info('bot connected')
                    self.setState('joiningRooms')
                else:
                    self.log.warn('could not connect to server - aborting.')
                    self.setState('disconnected')

            if self.getState() == 'disconnected':
                self.conn = None
                self.log.info('bot disconnected')
                if self.autoReconnect:
                    self.setState('connecting')

            if self.getState() == 'disconnecting':
                self.log.info('bot disconnecting')
                self._disconnect()
                self.setState('disconnected')

            if self.getState() == 'notstarted':
                pass

            sleep(1)
            
        self._shutdown()
        return 0

    def updateRosters(self):
        """
        This method update the bot roster (contact list)
        """
        self.roster = self.conn.Roster.getRoster()
        self.log.info('*** roster ***')
        i=0
        self.contactId = {}
        for contact in self.roster.getItems():
            contactId = '$' + str(i)
            self.contacts[contactId] = contact
            self.log.info('%s - %s' % (contactId, contact))
            i = i+1
        self.log.info('*** roster ***')

    def joinRoom(self, room, username=None, password=None):
        """
        Join the specified multi-user chat room (muc)
        @param room: Name of the muc
        @type room: string
        @param username: Username to use as room member
        @type username: string
        @param password: Password to use when the muc is password protected
        @type password: string
        """
        NS_MUC = 'http://jabber.org/protocol/muc'
        self.log.info('Joining room: ' + room)

        if username is None:
            username = self._username.split('@')[0]
        room_jid = '/'.join((room, username))
        pres = xmpp.Presence(to=room_jid)

        self.log.debug("*** room = %s" % room)
        self.log.debug("*** room_jid = %s" % room_jid)
        self.log.debug("*** username = %s" % username)
        self.log.info("%s entered room %s" % (username, room))

        if password is not None:
            pres.setTag('x',namespace=NS_MUC).setTagData('password',password)
        
        if room not in self._joinedRooms:
            self._joinedRooms.append(room)

        self.conn.send(pres)

    def inviteToRoom(self, users, room=None, username=None, msg='Hello there!'):
        """
        Invite a user to a room
        @param users: List of users to invite
        @type users: List
        @param room: Room to join
        @type room: string
        @param username: Username to use once in the room (for the bot)
        @type username: string
        @param msg: 
        """
        NS_MUCUSER = 'http://jabber.org/protocol/muc#user'
        self.log.info('Inviting ' + str(users))

        if room is None:
            node = self.jid.getNode()
            domain = self._botConfig.get('bot', 'muc-domain')
            #domain = self.GMAIL_MUC_DOMAIN
            room = node + '@' + domain

        if username is None:
            username = self._username.split('@')[0]
        room_jid = '/'.join((room, username))
        pres = xmpp.Presence(to=room_jid)
        self.conn.send(pres)

        self.log.debug("*** room = %s" % room)
        self.log.debug("*** room_jid = %s" % room_jid)
        self.log.debug("*** username = %s" % username)
        self.log.info("%s entered room %s" % (username, room))

        oInvMsg = xmpp.protocol.Message(body=msg)
        oInvMsg.setTo(room)
        oInvMsg.setType('groupchat')
        self.conn.send(oInvMsg)

        for u in users:
            self.log.info('Inviting: ' + u)
            invite = xmpp.simplexml.Node('invite')
            invite.setAttr('to', u)
            invite.setTagData('reason', msg) 
            mess = xmpp.protocol.Message(to=room)
            mess.setTag('x', namespace=NS_MUCUSER).addChild(node=invite)
            self.conn.send(mess)

        # tests
        #self.getRoomMembers(room)

    # http://xmpp.org/extensions/xep-0045.html#disco-roominfo
    #<iq from='hag66@shakespeare.lit/pda'
    #    id='kl2fax27'
    #    to='coven@chat.shakespeare.lit'
    #    type='get'>
    #  <query xmlns='http://jabber.org/protocol/disco#items'/>
    #</iq>
    
    # reply
    #<iq from='coven@chat.shakespeare.lit'
    #    id='kl2fax27'
    #    to='hag66@shakespeare.lit/pda'
    #    type='result'>
    #  <query xmlns='http://jabber.org/protocol/disco#items'>
    #    <item jid='coven@chat.shakespeare.lit/firstwitch'/>
    #    <item jid='coven@chat.shakespeare.lit/secondwitch'/>
    #  </query>
    #</iq>
    def getRoomMembers(self,room):
        """
        Query a server to obtain the list of members in a room
        @param room: room to query members
        @type room: string
        """
        NS_DISCO_ITEMS = 'http://jabber.org/protocol/disco#items'
        self.log.info('Listing room members for: ' + room)

        username = self._username.split('@')[0]
        room_jid = '/'.join((room, username))
        #iq = xmpp.Protocol('iq', typ='get', payload=[xmpp.Node('query', attrs={'xmlns':NS_DISCO_ITEMS})])
        iq = xmpp.Iq(to=room,typ='get')
        #iq.setAttr('id', '1001')
        iq.setFrom(self.jid)
        iq.addChild('query', namespace=NS_DISCO_ITEMS)

        self.log.debug("*** room = %s" % room)
        self.log.debug("*** room_jid = %s" % room_jid)
        self.log.debug("*** username = %s" % username)

        print 'GET ROOM MEMBER: ' + str(iq)
        self._connect().send(iq)
        #res = self.conn.SendAndWaitForResponse(iq, 3)
        #print 'RESULT OF GET ROOM MEMBER: ' + str(res)

    def sendFile(self, jid, sFile, sData=None):
        """
        Send a file to a user. Note that this is really slow. 
        @note: THIS IS NOT WORKING! Don't use it.
        @param jid: JID of the destination user
        @type jid: JID
        @param sFile: File path (Must be absolute)
        @type sFile: string
        @param sData: Data stream to send (set sFile to None to send this way)
        @type sData: string
        """
        try:
            if sFile and sFile.startswith('/') and \
                 not sFile.startswith('/dev') and \
                 not sFile.startswith('/proc') and \
                 not sFile.startswith('/sys'):
                f = open(sFile)
            elif sData != None:
                f = StringIO.StringIO()
                f.write('String data')
                f.close()
            else:
                f = None
            self.ibb.OpenStream('123', jid, f) 
        except Exception,e:
            self.log.error('Could not send file')
            self.log.exception(e)

    def send_message(self, mess):
        """
        Send an XMPP message
        @param mess: A message
        @type mess: Object
        """
        self.conn.send(mess)

    def send_tune(self, song, debug=False):
        """
        Set information about the currently played tune
        Song is a dictionary with keys: file, title, artist, album, pos, track, length, uri. For details see <http://xmpp.org/protocols/tune/>.
        @param song: Song information to display
        @type song: Dictionnary
        @param debug: Debug flag
        @type debug: bool
        """
        NS_TUNE = 'http://jabber.org/protocol/tune'
        iq = xmpp.Iq(typ='set')
        iq.setFrom(self.jid)
        iq.pubsub = iq.addChild('pubsub', namespace=xmpp.NS_PUBSUB)
        iq.pubsub.publish = iq.pubsub.addChild('publish', attrs={ 'node' : NS_TUNE })
        iq.pubsub.publish.item = iq.pubsub.publish.addChild('item', attrs={ 'id' : 'current' })
        tune = iq.pubsub.publish.item.addChild('tune')
        tune.setNamespace(NS_TUNE)

        title = None
        if song.has_key('title'):
            title = song['title']
        elif song.has_key('file'):
            title = os.path.splitext(os.path.basename(song['file']))[0]
        if title is not None:
            tune.addChild('title').addData(title)
        if song.has_key('artist'):
            tune.addChild('artist').addData(song['artist'])
        if song.has_key('album'):
            tune.addChild('source').addData(song['album'])
        if song.has_key('pos') and song['pos'] > 0:
            tune.addChild('track').addData(str(song['pos']))
        if song.has_key('time'):
            tune.addChild('length').addData(str(song['time']))
        if song.has_key('uri'):
            tune.addChild('uri').addData(song['uri'])

        if debug:
            self.log.info('Sending tune: %s' % iq.__str__().encode('utf8'))
        self.conn.send(iq)

    def send(self, user, text, in_reply_to=None, message_type='chat'):
        """
        Sends a simple message to the specified user, in private.
        @param user: User to send the message
        @type user: string
        @param text: Message to send
        @type text: string
        @param in_reply_to: [optional] If the message is a reply, this var should contain the username to send back
        @type in_reply_to: string
        @param message_type: [optional] Determine if this is a chat or groupchat message
        @type message_type: string
        """
        mess = self.build_message(text)
        mess.setTo(user)

        if in_reply_to:
            mess.setThread(in_reply_to.getThread())
            mess.setType(in_reply_to.getType())
        else:
            mess.setThread(self._threads.get(user, None))
            mess.setType(message_type)

        self.send_message(mess)

    def send_simple_reply(self, mess, text, private=False):
        """
        Send a simple response to a message
        @param mess: Message Object 
        @type mess: Object
        @param text: Message sent, triggering a reply
        @type text: string
        @param private: Determine if the reply is private. A private answer is sent to a user only, not a groupchat
        @type private: bool
        """
        self.send_message(self.build_reply(mess, text, private))

    def build_reply(self, mess, text=None, private=False):
        """
        Build a message for responding to another message.  Message is NOT sent
        @param mess: Message Object 
        @type mess: Object
        @param text: Message sent, triggering a reply
        @type text: string
        @param private: Determine if the reply is private. A private answer is sent to a user only, not a groupchat
        @type private: bool
        """
        response = self.build_message(text)
        if private:
            response.setTo(mess.getFrom())
            response.setType('chat')
        else:
            response.setTo(mess.getFrom().getStripped())
            response.setType(mess.getType())
        response.setThread(mess.getThread())
        return response

    def build_message(self, text):
        """
        Builds an xhtml message without attributes. If input is not valid xhtml-im fallback to normal.
        @param text: Text to use as message body
        @type text: string
        """
        if text == None: text = ''
        message = None # fixes local variable 'message' referenced before assignment - Thanks to Aleksandr
        text_plain = re.sub(r'<[^>]+>', '', text) # Try to determine if text has xhtml-tags - TODO needs improvement
        if text_plain != text:
            message = xmpp.protocol.Message(body=text_plain) # Create body w stripped tags for reciptiens w/o xhtml-abilities - FIXME unescape &quot; etc.
            html = xmpp.Node('html', {'xmlns': 'http://jabber.org/protocol/xhtml-im'}) # Start creating a xhtml body
            try:
                html.addChild(node=xmpp.simplexml.XML2Node("<body xmlns='http://www.w3.org/1999/xhtml'>" + text.encode('utf-8') + "</body>"))
                message.addChild(node=html)
            except Exception, e:
                # Didn't work, incorrect markup or something.
                self.log.debug('An error while building a xhtml message. Fallback to normal messagebody')
                message = None # Fallback - don't sanitize invalid input. User is responsible!
        if message is None:
            message = xmpp.protocol.Message(body=text) # Normal body
        return message

    def get_sender_username(self, mess):
        """
        Extract the sender's user name from a message
        @param mess: Message Object 
        @type mess: Object
        """
        type = mess.getType()
        jid = mess.getFrom()
        if type == "groupchat":
            username = jid.getResource()
        elif type == "chat":
            username = jid.getNode()
        else:
            username = ""
        return username

    def broadcast(self, message, only_available=False):
        """
        Broadcast a message to all users 'seen' by this bot.
        If the parameter 'only_available' is True, the broadcast will not go to users whose status is not 'Available'.
        @param message: Message to broadcast
        @type message: string
        @param only_available: [optional] Determine if the message must be sent only to available users.
        @type only_available: bool
        """
        for jid, (show, status) in self._seen.items():
            if not only_available or show is self.AVAILABLE:
                self.send(jid, message)

    def idle_proc(self):
        """
        This function will be called in the main loop.
        """
        self._idle_ping()

    def isValidDomain(self, domain):
        """
        Determine if a domain is valid for this connection (Ex: for xmpp, there are muc domains (gmail.com) and user domains (talk.google.com))
        @param domain: The domain to check
        @type domain: string
        """
        if (self.jid \
            and domain == str(self.jid.getDomain()))\
            or (self._botConfig.has_option('bot', 'muc-domain')\
            and domain == self._botConfig.get('bot', 'muc-domain')):
            return True
        else:
            return False

