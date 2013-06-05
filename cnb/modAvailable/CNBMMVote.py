#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - Vote
'''

import datetime
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMVote(CNBMatrixModule):
    """

    """

    name = 'vote'
    usage = ''
    desc = 'Detect vote patterns, accumulate answers and print results'
    enProcessCmd = True
    enProcessPattern = True
    
    PVOTE_SUFFIX = '++'
    NVOTE_SUFFIX = '--'
    _votes = []

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        self._initOptParser()
        
    def __del__(self):
        pass

    def _initOptParser(self):
        CNBMatrixModule._initOptParser(self)

        self.parser.add_argument('-a', '--all', action='store_true', dest='all', default=False,
                      help='List all daily vote string')
        self.parser.add_argument('string', metavar='VOTE_STRING', action='store', default='',\
                      help='Quote to search for', nargs='*')

    def _submitVote(self,room,username,quote,vote):
        date = datetime.datetime.today().date()
        o = {'date': date, 'room': str(room), 'username': str(username), 'quote': str(quote), 'vote': str(vote)}
        self.log.info('Voting: ' + str(o))
        self._votes.append(o)

    def _getCompiledVotes(self,room,quote=None):
        date = datetime.datetime.today().date()
        res = {}
        for oVote in self._votes:
            if date == oVote['date']\
               and oVote['room'] == room \
               and ((quote and oVote['quote'] == quote) or not quote):
                if not (oVote['quote'] in res):
                    res[oVote['quote']] = {}
                    res[oVote['quote']][self.PVOTE_SUFFIX] = 0
                    res[oVote['quote']][self.NVOTE_SUFFIX] = 0
                if oVote['vote'] == self.PVOTE_SUFFIX:
                    res[oVote['quote']][self.PVOTE_SUFFIX] += 1
                elif oVote['vote'] == self.NVOTE_SUFFIX:
                    res[oVote['quote']][self.NVOTE_SUFFIX] += 1
        return res
                
    def _getVotesOutput(self,room,quote=None):
        votes = self._getCompiledVotes(room,quote)
        result = ''
        for q,v in votes.iteritems():
            t = v[self.PVOTE_SUFFIX] + v[self.NVOTE_SUFFIX]
            result = result + str(q) + ': UP(' + str(v[self.PVOTE_SUFFIX]) + '), DOWN(' + str(v[self.NVOTE_SUFFIX]) + '), TOTAL(' + str(t) + ')' + "\n"
        return result

    def checkPattern(self,oMsg):
        if oMsg.text \
           and (oMsg.text.endswith(self.PVOTE_SUFFIX) \
           or oMsg.text.endswith(self.NVOTE_SUFFIX)) \
           and not oMsg.isPrivate:
            return True
        else:
            return False
                
    def processPattern(self,oMsg):
        if oMsg.text.endswith(self.PVOTE_SUFFIX):
            q = oMsg.text.split(self.PVOTE_SUFFIX,1)[0]
            v = self.PVOTE_SUFFIX
        elif oMsg.text.endswith(self.NVOTE_SUFFIX):
            q = oMsg.text.split(self.NVOTE_SUFFIX,1)[0]
            v = self.NVOTE_SUFFIX
        r = oMsg.room
        u = oMsg.username

        self._submitVote(r,u,q,v)

    def processCmd(self,oMsg):
        result = 'Missing arguments, check help'
        (args, err) = self.getParsedArgs(oMsg.args)

        if args.string != '':
            s = ' '.join(args.string)
        else:
            s = None

        if err != '':
            result = err
        elif args.all: 
            if not oMsg.isPrivate:
                room = str(oMsg.room)
                result = self._getVotesOutput(room)
            else:
                result = ''
        elif s != '':
            if not oMsg.isPrivate:
                room = str(oMsg.room)
                result = self._getVotesOutput(room, s)
            else:
                result = ''
        elif args.help:
            result = self.getUsage()
        else:
            result = self.getUsage()

        return result
