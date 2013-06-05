#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - spy
'''

from cnb.cnbConfig import CNBConfig
from cnb.cnbManager import CNBManager
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMSpy(CNBMatrixModule):
    """

    """

    name = 'spy'
    usage = ''
    desc = 'Useful module to centralize what\'s being said on the internet...'
    aliases = []
    isAdmin = True
    enProcessCmd = True
    enProcessPattern = True

    _spyRules = {}


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        self._initOptParser()
        self._initDefaultRules()

    def __del__(self):
        pass

    def _initOptParser(self):
        CNBMatrixModule._initOptParser(self)

        self.parser.add_argument('-l', '--list', action='store_true', dest='mod_list', default=False,
                      help='[mode] List current spying rules')
        self.parser.add_argument('-a', '--add', action='store_true', dest='mod_add', default=False,
                      help='[mode] Add a spying rule')
        self.parser.add_argument('-d', '--delete', action='store_true', dest='mod_del', default=False,
                      help='[mode] Add a spying rule')
        self.parser.add_argument('--src', action='store', dest='src', default='',
                      help='Specify a list of source')
        self.parser.add_argument('--dst', action='store', dest='dst', default='',
                      help='Specify a list of destination')

    def _initDefaultRules(self):
        oConfig = CNBConfig.getInstance()
        if oConfig.has_option('spy', 'rules'):
            self.log.info('Importing default rules')
            aRules = oConfig.get('spy', 'rules')
            for r in aRules:
                aSrcDst = r.split('->')
                if len(aSrcDst) == 2:
                    aSrc = aSrcDst[0].split(';')
                    aDst = aSrcDst[1].split(';')
                    self.addRule(aSrc,aDst)

    def _send(self, oMsg, conId, dst):
        sMsg = '[' + oMsg.getFullSource() + '] ' + str(oMsg.text)
        oConMgr = CNBManager.getInstance()
        result = oConMgr.sayCNB(conId,dst,sMsg)

    def listRules(self):
        result = "List of spy rules:\n"
        for dst,srcDict in self._spyRules.iteritems():
            for src in srcDict['list']:
                result += "  " + src + " -> " + dst + "\n"
        return result

    def addRule(self, aSrcList, aDstList):
        """
        """
        result = ''
        for dst in aDstList:
            dst = str(dst)
            if len(dst.split('@')) > 1:
                dom = str(dst.split('@')[1])
                if not self._spyRules.has_key(dst):
                    self._spyRules[dst] = {}
                    self._spyRules[dst]['list'] = set()
                    self._spyRules[dst]['conId'] = None
        
                oMgr = CNBManager.getInstance()
                conId = oMgr.getConIdCNB(dom)
                if conId:
                    self._spyRules[dst]['list'].update(aSrcList)
                    self._spyRules[dst]['conId'] = conId
                    for src in aSrcList:
                        src = str(src)
                        result += '%s -> %s rule was added successfuly' % (src,dst)
                else:
                    result += "The destination address ""%s"" could not be found \n" % dst
            else:
                result += "The destination address ""%s"" is invalid \n" % dst
        return result

    def delRule(self, aSrcList, aDstList):
        result = 'rule deleted.'
        for dst in aDstList:
            for src in aSrcList:
                if self._spyRules.has_key(dst) and src in self._spyRules[dst]:
                    self._spyRules[dst]['list'].remove(src)
                    if len(self._spyRules[dst]['list']) == 0:
                        del(self._spyRules[dst]['list'])
                        del(self._spyRules[dst]['conId'])
                        del(self._spyRules[dst])
        return result

    def processCmd(self, oMsg):
        result = 'Missing arguments, check help'
        (opts, args) = self.parser.parse_args(oMsg.args)
        if opts.mod_list:
            return self.listRules()
        elif opts.mod_add and opts.src and opts.dst:
            aSrc = str(opts.src).split(',')
            aDst = str(opts.dst).split(',')
            return self.addRule(aSrc,aDst)
        elif opts.mod_del:
            aSrc = str(opts.src).split(',')
            aDst = str(opts.dst).split(',')
            return self.delRule(aSrc,aDst)
        else:
            return result

    def checkPattern(self,oMsg):
        if oMsg.text != None:
            sSrc = oMsg.getSource()
            for dst,srcObj in self._spyRules.iteritems():
                if sSrc in srcObj['list']:
                    return True
        return False

    def processPattern(self,oMsg):
        sSrc = oMsg.getSource()
        for dst,srcObj in self._spyRules.iteritems():
            if sSrc in srcObj['list']:
                self._send(oMsg,srcObj['conId'],dst)

