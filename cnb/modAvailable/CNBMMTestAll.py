#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - test all
'''

from time import sleep
from cnb.cnbManager import CNBManager
from cnb.cnbMatrix import CNBMatrix
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMTestAll(CNBMatrixModule):
    """

    """

    name = 'testall'
    usage = 'testall'
    desc = 'This command let you test a shit load of modules'
    aliases = []
    isAdmin = True
    hidden = True

    _allCmds = ['.fact', '.fact fr', '.fact en', '.fact SOMETHINGELSE', \
                '.help', '.botinfo', '.weather', \
                '.nmap', '.nmap 127.0.0.1', \
                '.hash', '.hash md5', '.hash asdf', '.hash md5 password','.hash sha1 password',\
                '.hash sha256 password','.hash sha512 password',
                '.crack', '.crack asdf', '.crack md5 21232f297a57a5a743894a0e4a801fc3', \
                '.encode', '.encode Tamere!', \
                '.tamere', '.tamere asdf', \
                '.chuckkukdo', '.chuckkukdo asdf', \
                '.surf', '.surf asdf', '.surf www.google.com', \
                '.mods']
    _xmppCmds = ['.say asdf', '.say asdf asdf', '.say martin.dube@gmail.com', '.say martin.dube@gmail.com TestAll', \
                 '.mondaysuck', \
                 '.vn', '.pat']
    _ircCmds = ['.say asdf', '.say asdf asdf', '.say mdube TestAll', '.say #pyrofreak TestAll', \
                '.join asdf', '.join #pyrofreak']

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        oMatrix = CNBMatrix.getInstance()
        oMgr = CNBManager.getInstance()

        sUser = oMsg.jid
        prot = oMsg.protocol
        sInitCmd = oMsg.cmd
        sInitArgs = oMsg.args

        # For all protocols
        for sCmd in self._allCmds:
            oMsg.text = sCmd
            oMsg.initCmd()
            if prot.startswith('xmpp'):
                result = 'cmd: ' + sCmd + "\nresult: " + oMatrix.processXmppMod(oMsg)
            elif prot.startswith('irc'):
                result = 'cmd: ' + sCmd + "\nresult: " + oMatrix.processIrcMod(oMsg)
            oMgr.sayCNB(oMsg.conId,sUser,result)
            sleep(1)

        # For xmpp only
        for sCmd in self._xmppCmds:
            oMsg.text = sCmd
            oMsg.initCmd()
            if prot.startswith('xmpp'):
                result = 'cmd: ' + sCmd + "\nresult: " + oMatrix.processXmppMod(oMsg)
            oMgr.sayCNB(oMsg.conId,sUser,result)
            sleep(1)

        # For irc only
        for sCmd in self._ircCmds:
            oMsg.text = sCmd
            oMsg.initCmd()
            if prot.startswith('irc'):
                result = 'cmd: ' + sCmd + "\nresult: " + oMatrix.processIrcMod(oMsg)
            oMgr.sayCNB(oMsg.conId,sUser,result)
            sleep(1)

        return ''
