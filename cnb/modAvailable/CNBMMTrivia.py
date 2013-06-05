#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module
'''

import os
import re
import sys
import random
import logging
import csv
import pickle
import argparse
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime,timedelta
from time import sleep
from threading import Thread
from cnb.cnbConfig import CNBConfig
from cnb.cnbManager import CNBManager
from cnb.cnbMatrix import CNBMatrix
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMTrivia(CNBMatrixModule):
    """

    """

    # Bot vars
    name = 'trivia'
    usage = ''
    desc = 'This cmd let you play or manage the trivia game'
    aliases = ['t']
    isAdmin = False
    
    _aGameInst = {}
    _aLocalUsers = {'irc.freenode.net': ['mdube', 'vn', 'gparent', 'patoff'],\
                    'irc.hf': ['mdube', 'vn', 'gparent', 'patoff'],\
                    'conference.hackfest.ca': ['martin'],\
                    'hackfest.ca': ['martin']}

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        self._initOptParser()
        
    def __del__(self):
        self.stopAllGames()

    def _initOptParser(self):
        CNBMatrixModule._initOptParser(self,False)

        genGrp = self.parser.add_argument_group("General Options", "These are participants commands")
        admGrp = self.parser.add_argument_group("Admin Options", "These are for HF crew only (no there is no hack in there)")

        genGrp.add_argument("-h", "--help", action="store_true", dest='help', default=False,\
                      help='Display help')
        genGrp.add_argument('-s', '--submit', action='store', dest='answer', default='',\
                      help='Submit an answer', nargs='+')
        genGrp.add_argument('-q', '--question', action='store_true', dest='question', default=False,\
                      help='Repeat the actual question')
        genGrp.add_argument('--score', action='store_true',  dest='score', default=False,\
                      help='Print actual trivia score')

        admGrp.add_argument('--start', action='store_true', dest='adm_start', default=False,
                      help='[adm] Start the trivia game')
        admGrp.add_argument('--start-time', action='store', dest='adm_starttime', default='',
                      help='[adm] Start the trivia game at a specific time (format: YYYY-MM-DD_HH:MM)')
        admGrp.add_argument('--stop', action='store_true', dest='adm_stop', default=False,
                      help='[adm] Stop the trivia game')
        admGrp.add_argument('-n', '--next', action='store_true', dest='adm_next', default='',
                      help='[adm] Change to next question')
        admGrp.add_argument('--save', action='store_true', dest='adm_save', default=0,
                      help='[adm] Save the bot state')
        admGrp.add_argument('--load', action='store_true', dest='adm_load', default=0,
                      help='[adm] Load the bot state')
        admGrp.add_argument('--status', action='store_true', dest='adm_status', default=False,
                      help='[adm] Print actual trivia status')
        admGrp.add_argument('-i', '--qinfo', action='store', dest='adm_qinfo', type=int, default=0,
                      help='[adm] Print question information (answer, flags, etc.)', nargs=1)

    def _isAllowed(self, acl, user, domain, args):
        if args.adm_start or args.adm_stop or \
           args.adm_next or args.adm_status or args.adm_qinfo or \
           args.adm_save or args.adm_load:
            oMatrix = CNBMatrix.getInstance()
            if oMatrix.isAllowed(acl, user, domain):
                return True
            else:
                return False
        else:
            return True

    def processCmd(self, oMsg):
        result = 'Missing arguments, check help'
        (args, err) = self.getParsedArgs(oMsg.args)

        globalConfig = CNBConfig.getInstance()
        oMgr = CNBManager.getInstance()
        instConfig = oMgr.getConfigCNB(oMsg.conId)
        if self._aGameInst.has_key(oMsg.conId):
            oGame = self._aGameInst[oMsg.conId]
        else:
            oGame = None
        
        if self._isAllowed(self._aLocalUsers, oMsg.username, oMsg.domain, args):    
            if err != '':
                result = err
            elif args.adm_start:
                if not oGame:
                    if not oMsg.isPrivate:
                        oGame = CNBMMTriviaGame(oMsg.conId,oMsg.room)
                        self._aGameInst[oMsg.conId] = oGame
                        result = 'Starting the trivia game'
                    else:
                        result = 'You must start trivia in a public room/chan'
                else:
                    result = 'Game already started'
            elif args.adm_starttime:
                if not oGame:
                    if not oMsg.isPrivate:
                        try:
                            f = '%Y-%m-%d_%H:%M'
                            v = ' '.join(args.adm_starttime)
                            d = datetime.strptime(v, f)
                            isValid = (v == d.strftime(f)) # this makes sure the parsed date matches the original string
                        except ValueError:
                            isValid = False
                        if isValid:
                            oGame = CNBMMTriviaGame(oMsg.conId,oMsg.room,d)
                            self._aGameInst[oMsg.conId] = oGame
                            result = 'Game will start on ' + str(args.adm_starttime)
                        else:
                            result = 'Bad date/time format'
                    else:
                        result = 'You must start trivia in a public room/chan'
                else:
                    result = 'Game already started'
            elif args.adm_stop: 
                if oGame:
                    if not oMsg.isPrivate:
                        oGame.stopTrivia()
                        del oGame
                        oGame = None
                        self._aGameInst.pop(oMsg.conId)
                        result = 'Stopping...'
                    else:
                        result = 'You must stop trivia in a public room/chan'
                else:
                    result = 'Game not started yet'
            elif args.adm_next:
                if oGame:
                    oGame.chgQt()
                    result = ''
                else:
                    result = 'Game not started yet'
            elif args.adm_save:
                if oGame:
                    result = oGame.save()
                else:
                    result = 'Game not started yet'
            elif args.adm_load:
                if oGame:
                    result = oGame.load()
                else:
                    result = 'Game not started yet'
            elif args.adm_status:
                if oGame:
                    result = oGame.getStatus()
                else:
                    result = 'Game not started yet'
            elif args.adm_qinfo:
                if oGame:
                    if oMsg.isPrivate:
                        v = args.adm_qinfo[0]
                        result = oGame.getQuestionInfo(v)
                    else:
                        result = 'You must submit in private'
                else:
                    result = 'Game not started yet'
            elif args.answer:
                if oGame: 
                    if oMsg.isPrivate:
                        v = ' '.join(args.answer)
                        result = oGame.submitAnswer(oMsg.username, v)
                        #result = oGame.submitAnswer(oMsg.username, args.answer)
                    else:
                        result = 'You must submit in private'
                else:
                    result = 'Game not started yet'
            elif args.question: 
                if oGame:
                    result = oGame.getCurQtMsg()
                else:
                    result = 'Game not started yet'
            elif args.score: 
                if oGame:
                    result = "Score: \n" + oGame.getResult()
                else:
                    result = 'Game not started yet'
            elif args.help:
                result = self.getUsage()
            else:
                result = self.getUsage()
        else:
            result = 'Unauthorized :)'

        return result

    def stopAllGames(self):
        self.log.info('Killing trivia threads')
        for k,oGame in self._aGameInst.iteritems():
            oGame.stopTrivia()

class CNBMMTriviaGame(Thread):
    """

    """

    # Vars
    curQtId = 0
    startDateTime = None
    beginDateTime = None
    qtDateTime = None
    autoSave = True
    _conId = None
    _room = None
    _state = 'notstarted'
    _questions = []
    _results = {}
    _dateFormat = '%Y-%m-%d_%H:%M'
    TRIVIA_QUESTIONS_FILE = 'trivia.ihn2k13.csv'
    TRIVIA_SAVE_FILE = 'trivia.state.bin'

    def __init__(self,conId,room,stime=None,load=None):
        Thread.__init__(self)
        oConfig = CNBConfig.getInstance()
        self.log = logging.getLogger(self.__class__.__name__)
        self._configLogs(oConfig)
        
        self._conId = conId
        self._room = room
        if stime:
            self.startDateTime = stime
            self.startAndWaitTrivia()
        else:
            self.startTrivia()

        sRootDir = oConfig.get('global', 'trivia-dir')
        self._importQts(sRootDir + self.TRIVIA_QUESTIONS_FILE)

        if load:
            self.load()

        self.start()

    def __del__(self):
        del self.log
        pass

    def _shutdown(self):
        """This function will be called when we're done serving

        Override this method in derived class if you
        want to do anything special at _shutdown.
        """
        self.log.info('Going down')
    
    def _start(self):
        self.log.info('Starting trivia game')
        self.log.info(self.getCurQtMsg().replace("\n", ', '))
        self.printInstructions()
        sleep(2)
        for x in range(0, 3):
            self.sayTrivia(str(3-x))
            sleep(1)
        self.qtDateTime = datetime.today()
        self.printCurQt()

    def _stop(self):
        self.log.info('Stopping trivia game')
        self.printEndMsg()

    def _importQts(self,qtFile):
        self.log.info('Imported Trivia questions file: ' + qtFile)

        with open(qtFile, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for q in reader:
                if len(q) > 0 and len(q[0]) > 0 and q[0][0] != '#':    #assuming no blank lines
                    iId = int(q[0])
                    sQuestion = str(q[1]).lower()
                    if q[2][0] == '[' and q[2][len(q[2])-1] == ']':
                        #self.log.info(str(q[2][1:-1]))
                        aAnswer = (q[2][1:-1]).split(',')
                    else:
                        aAnswer = [q[2].lower()]
                    aAnswer = map(str.lower,aAnswer)
                    sFlag = str(q[3]).lower()
                    sValue = int(q[4])
                    sDuration = int(q[5]) * 60
                    #sDuration = int(q[5])
    
                    self._questions.append({'id':iId,'q':sQuestion,'a':aAnswer,'f':sFlag,'v':sValue,'d':sDuration})

        self.log.info(self._questions)

    def _configLogs(self, globalConfig):
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(globalConfig.get('global', 'log-format')))
        fh = TimedRotatingFileHandler(os.path.join(globalConfig.get('global', 'log-dir'), 'cnb-trivia.log'), backupCount=0, when='d', interval=1)
        fh.setFormatter(logging.Formatter(globalConfig.get('global', 'log-format')))
        fh.doRollover()
        
        logLevel = logging.DEBUG
    
        self.log.addHandler(ch)
        self.log.addHandler(fh)
        self.log.setLevel(logLevel)
    
    def run(self):

        while self.isRunning():
            if self.getState() == 'waiting':
                if self.getRemainingStartTime() <= 0:
                    self.startTrivia()
            elif self.getState() == 'starting':
                self.beginDateTime = datetime.today()
                self._start()
                self.setState('running')

            elif self.getState() == 'running':
                r = self.getRemainingQtTime()
                if r < 0:
                    if self.autoSave:
                        self.save()

                    if self.getRemainingQtCount() > 1:
                        self.log.info('Time is exhausted, changing question')
                        self.sayTrivia('Time is exhausted, changing question')
                        self.chgQt()
                    elif self.getRemainingQtCount() == 1:
                        self.log.info('Final question!')
                        self.sayTrivia('Final question!')
                        self.chgQt()
                    elif self.getRemainingQtCount() == 0:
                        self.stopTrivia()

            elif self.getState() == 'stopping':
                self._stop()
                self.setState('stopped')

            elif self.getState() == 'stopped':
                break

            sleep(1)
        
        # When loop is done, shutdown
        self._shutdown()
        return 0

    def getState(self):
        return self._state

    def setState(self, state):
        self.log.info('New state: ' + self._state)
        self._state = state

    def isRunning(self):
        if (self._state in ['waiting','starting','running','stopping','stopped']):
            return True
        else:
            return False

    def startTrivia(self):
        self.setState('starting')
    
    def startAndWaitTrivia(self):
        self.setState('waiting')

    def stopTrivia(self):
        self.setState('stopping')

    def submitAnswer(self,user,answer):
        self.log.info('"' + str(user) + '" submited "' + str(answer.lower()) + '" for question "#' + str(self.curQtId) + '"')
        result = ''
        if str(answer.lower()) in self._questions[self.curQtId]['a']:
            self.goodAnswer(user)
            result = 'Flag: ' + self._questions[self.curQtId]['f']
        if result == '':
            result = 'Nop... :)'
        return result

    def goodAnswer(self,user):
        self.log.info('"' + str(user) + '" submited a good answer for question "' + str(self.curQtId) + '"')
        if not self._results.has_key(user):
            self._results[user] = set()
        if not self.curQtId in self._results[user]:
            self._results[user].add(self.curQtId)

    def getCurQt(self):
        return self._questions[self.curQtId]['q']

    def getCurDur(self):
        return self._questions[self.curQtId]['d']

    def getCurQtMsg(self):
        return 'ID: ' + str(self.curQtId) + "\nDuration: " + str(timedelta(seconds=self.getCurDur())) + "\nQuestion: " + str(self.getCurQt())

    def chgQt(self):
        self.log.info('Changing question (Remaining: ' + str(self.getRemainingQtCount()) + ')')
        self.log.info(self.getCurQtMsg().replace("\n", ', '))
        if self.getRemainingQtCount() > 0:
            self.qtDateTime = datetime.today()
            self.curQtId = self.curQtId + 1
            self.printCurQt()

    def getRemainingStartTime(self):
        if self.startDateTime > datetime.today():
            d = self.startDateTime - datetime.today()
            self.log.debug('Remaining time before starting: ' + str(timedelta(seconds=d.seconds)))
            return d.seconds
        else:
            return -1

    def getRemainingQtTime(self):
        i = self.getCurDur()
        d = datetime.today() - self.qtDateTime
        r = i - d.seconds
        if r % 60 == 0:
            self.log.debug('Remaining question time: ' + str(timedelta(seconds=r)))
        #self.log.debug('Remaining question time: ' + str(r))
        return r

    def getRemainingQtCount(self):
        return len(self._questions) - (self.curQtId + 1)

    def getTotalGameTime(self):
        t = 0
        for q in self._questions:
            t += q['d']
        return t

    def getStatus(self):
        self.log.info('Getting some status')
        result = 'Here are some informations about trivia.\n\
        Trivia state: ' + str(self.getState()) + '\n\
        Nb of questions: ' + str(len(self._questions)) + '\n\
        Current Time: ' + str(datetime.today()) + '\n\
        Start Time: ' + str(self.startDateTime) + '\n'

        if self.getState() == 'waiting':
            result += '\
        Remaining time before starting the game: ' + str(self.getRemainingStartTime()) + '\n'

        if self.getState() == 'running':
            result += '\
        Nb of remaining questions: ' + str(self.getRemainingQtCount()) + '\n\
        Current question: [' + str(self.curQtId) + '] ' + self.getCurQt() + '\n\
        Time since the game started: ' + str(datetime.today() - self.beginDateTime) + '\n\
        Remaining time before changing question: ' + str(timedelta(seconds=self.getRemainingQtTime())) + '\n\
        Total game duration: ' + str(timedelta(seconds=self.getTotalGameTime())) + '\n\
        Score: \n' + str(self.getResult())
        return result

    def getResult(self):
        self.log.info('Getting results')
        result = ''
        spacer = '          '
        if len(self._results) > 0:
            for u,qts in self._results.iteritems():
                score = self.getUserTotal(qts)
                result += spacer + str(u) + ': ' + str(','.join(map(str,qts))) + ' (' + str(score) + 'pts)' '\n'
        else:
            result = spacer + '<Empty>'
        return result

    def getQuestionInfo(self, qId):
        result = ''
        qId = int(qId)
        if qId >= 0 and qId < len(self._questions):
            result = '\
                     ID: ' + str(qId) + "\n\
                     Duration: " + str(timedelta(seconds=self._questions[qId]['d'])) + "\n\
                     Question: " + str(self._questions[qId]['q']) + "\n\
                     Answer: " + str(self._questions[qId]['a']) + "\n\
                     Flag: " + str(self._questions[qId]['f']) + "\n\
                     Value: " + str(self._questions[qId]['v'])
        return result

    def getUserTotal(self,qts):
        score = 0
        for q in qts:
            score += self._questions[q]['v']           
        return score

    def sayTrivia(self,msg):
        oMgr = CNBManager.getInstance()
        return oMgr.sayCNB(self._conId,self._room,msg)

    def printCurQt(self):
        self.sayTrivia(self.getCurQtMsg())

    def printInstructions(self):
        msg = ''
        msg += "=============================\n"
        msg += "Concept\n"
        msg += "-------\n"
        msg += "Questions will be posted periodically for the whole night. Questions have a limited ttl (time to live) and must be answered during this ttl. For example, if a question is posted for a duration of 60 seconds, you have to answer within 60 seconds. Otherwise, game over for this flag.\n"
        msg += " \n"
        msg += "Instructions\n"
        msg += "------------\n"
        msg += "To submit answer, write in private: .trivia --submit=<ANSWER>\n"
        msg += "To repeat the actual question, write: .trivia --question\n"
        msg += "To get score, write: .trivia --score\n"
        msg += "For more, write: .trivia --help\n"
        msg += " \n"
        msg += "Don't forget to submit your flags in the scoreboard.\n"
        msg += " \n"
        msg += "Enjoy!\n"
        msg += " \n"
        msg += "=============================\n"
        self.sayTrivia(msg)
        
    def printEndMsg(self):
        msg = ''
        msg += "=============================\n"
        msg += "The trivia game has just ended. Thx for playing\n"
        msg += " \n"
        msg += "./gr33tz --to mart && vn && chuck\n"
        msg += " \n"
        msg += "Final score \n"
        msg += "----------- \n"
        msg += " \n"
        msg += self.getResult()
        msg += " \n"
        msg += "=============================\n"
        self.sayTrivia(msg)

    def save(self):
        oConfig = CNBConfig.getInstance()
        sFile = oConfig.get('global', 'log-dir') + self.TRIVIA_SAVE_FILE
        aObj = {'curQtId': self.curQtId,\
                'startDateTime': self.startDateTime,\
                'beginDateTime': self.beginDateTime,\
                'qtDateTime': self.qtDateTime,\
                'autoSave': self.autoSave,\
                #'_conId': self._conId,\
                #'_room': self._room,\
                '_state': self._state,\
                '_questions': self._questions,\
                '_results': self._results,\
                'timestamp': datetime.today(),\
               }
        self.log.info('Saving state to ' + sFile)
        pickle.dump(aObj, open(sFile, 'w'))
        return 'State was successfuly saved'

    def load(self):
        oConfig = CNBConfig.getInstance()
        sFile = oConfig.get('global', 'log-dir') + self.TRIVIA_SAVE_FILE
        self.log.info('Loading state from ' + sFile)
        aObj = pickle.load(open(sFile, 'r'))

        timestamp           = aObj['timestamp']
        self.curQtId        = aObj['curQtId']
        self.startDateTime  = aObj['startDateTime']
        #self.beginDateTime  = aObj['beginDateTime']
        self.beginDateTime  = datetime.today()
        self.qtDateTime     = aObj['qtDateTime'] + (datetime.today() - timestamp)
        self.autoSave       = aObj['autoSave']
        #self._conId         = aObj['_conId']
        #self._room          = aObj['_room']
        self._state         = aObj['_state']
        self._questions     = aObj['_questions']
        self._results       = aObj['_results']

        return 'State was successfuly loaded'

