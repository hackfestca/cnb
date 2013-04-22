#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - tamere
'''

# System imports
import random
from cnb.cnbConfig import CNBConfig
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMTaMere(CNBMatrixModule):
    """

    """

    name = 'tamere'
    usage = 'tamere'
    desc = 'Reply a funny joke about your mom :) Note that most of these jokes comes from Granby (Qc)'
    aliases = ['mom', 'mommy', 'yourmom']

    TAMERE_FACTS_FILE = 'tamere.txt'
    _tamereFacts = {}

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

        oConfig = CNBConfig.getInstance()
        sRootDir = oConfig.get('global', 'fact-dir')

        self.log.info('Imported Mother Quote file: ' + self.TAMERE_FACTS_FILE)
        fh = open(sRootDir + self.TAMERE_FACTS_FILE,"r")
        self._tamereFacts = fh.readlines()
        fh.close()

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        return self._tamereFacts[random.randint(1, len(self._tamereFacts)-1)].strip()


