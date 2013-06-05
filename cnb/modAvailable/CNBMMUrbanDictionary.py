#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - Urban Dictionary
'''

import json
import urllib2
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMUrbanDictionary(CNBMatrixModule):
    """

    """

    name = 'urbandictionary'
    usage = 'ud EXPRESSION'
    desc = 'This cmd ask Urban Dictionary for a description'
    aliases = ['ud']

    UD_URL = 'http://api.urbandictionary.com/v0/define?term=%s'
    HTTP_TIMEOUT = 5

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        self._initOptParser()

    def _initOptParser(self):
        CNBMatrixModule._initOptParser(self,False)

        self.parser.add_argument("-f", "--full", action="store_true", dest='full', default=False,\
                      help='Output full informations')
        self.parser.add_argument("-h", "--help", action="store_true", dest='help', default=False,\
                      help='Display help')
        self.parser.add_argument("-n", action="store", dest='n', type=int, default=0,\
                      help='Output a specific definition', nargs=1)
        self.parser.add_argument('string', metavar='STRING', action='store', default='',\
                      help='Text to search a definition', nargs='*')

    def _getOutput(self, r, n, f):
        result = ''
        if n == None:
            if f:
                for q in r['list']:
                    result += self._getFullQuote(q) + "\n"
            else:
                for q in r['list']:
                    result += self._getSimpleQuote(q) + "\n"
        else:
            q = r['list'][n]
            if f:
                result = self._getFullQuote(q)
            else:
                result = self._getSimpleQuote(q)

        return result

    def _getSimpleQuote(self, q):
        result = 'Def: ' + str(q['definition']) + "\n"\
                 'Word: ' + str(q['word']) + "\n"
        return result

    def _getFullQuote(self, q):
        result = 'Def: ' + str(q['definition']) + "\n"\
                 'Permalink: ' + str(q['permalink']) + "\n"\
                 'Word: ' + str(q['word']) + "\n"\
                 'Ranking (up/down): ' + str(q['thumbs_up']) + '/' + str(q['thumbs_down']) + "\n"\
                 'DefId: ' + str(q['defid']) + "\n"\
                 'Example: ' + str(q['example']) + "\n"
        return result
        
    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = 'Missing arguments, check help'
        (args, err) = self.getParsedArgs(oMsg.args)

        if args.string != '':
            s = ' '.join(args.string)
        else:
            s = ''

        if err != '':
            result = err
        elif args.help:
            result = self.getUsage()
        elif s != '':
            self.log.info('Searching for: ' + s)
            f = urllib2.urlopen(self.UD_URL % s,\
                                None,\
                                self.HTTP_TIMEOUT)
            if f:
                resp = json.loads(f.read())

                if args.n\
                   and len(args.n) == 1\
                   and 'list' in resp\
                   and args.n >= len(resp['list']):
                    n = args.n[0]
                else:
                    n = None

                if 'list' in resp \
                    and len(resp['list']) > 0:
                    result = self._getOutput(resp,n,args.full)
                else:
                    result = 'Could not find the expression'
            else:
                result = 'Could not execute query'
        return result
