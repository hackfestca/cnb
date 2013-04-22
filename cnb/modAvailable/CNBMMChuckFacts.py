#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module
'''

# System imports
import random
from cnb.cnbConfig import CNBConfig
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMChuckFacts(CNBMatrixModule):
    """

    """

    # Bot vars
    name = 'fact'
    usage = 'fact [LANG]'
    desc = 'This cmd simply is the truth!'
    aliases = ['chuckfact', 'facts', 'chuckfacts']

    CHUCK_FACTS_FILES = {'en': 'facts.en.txt', 'fr': 'facts.fr.txt'}
    _chuckFacts = {}

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        oConfig = CNBConfig.getInstance()
        sRootDir = oConfig.get('global', 'fact-dir')
        
        for k in self.CHUCK_FACTS_FILES:
            self.log.info('Imported Chuck Quote file: ' + self.CHUCK_FACTS_FILES[k])
            fh = open(sRootDir + self.CHUCK_FACTS_FILES[k],"r")
            self._chuckFacts[k] = fh.readlines()
            fh.close()

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        if len(oMsg.args) > 0 and oMsg.args[0] in self._chuckFacts:
            lang = oMsg.args[0]
            result = self._chuckFacts[lang][random.randint(1, len(self._chuckFacts[lang])-1)].strip()
        else:
            result = self._chuckFacts['en'][random.randint(1, len(self._chuckFacts['en'])-1)].strip()
        return result

