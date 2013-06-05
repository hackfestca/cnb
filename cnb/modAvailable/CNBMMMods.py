#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - mods
'''

from cnb.cnbMatrix import CNBMatrix
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMMods(CNBMatrixModule):
    """

    """

    name = 'mods'
    usage = ''
    desc = 'This cmd let you list and manage registered modules'
    aliases = ['mod', 'module']
    isAdmin = True

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        self._initOptParser()

    def __del__(self):
        pass

    def _initOptParser(self):
        CNBMatrixModule._initOptParser(self,False)

        self.parser.add_argument("-h", "--help", action="store_true", dest='help', default=False,\
                      help='Display help')
        self.parser.add_argument('--register', metavar='MODULE', action='store', dest='register', default='',\
                      help='Register a module', nargs=1)
        self.parser.add_argument('--unregister', metavar='MODULE', action='store', dest='unregister', default='',\
                      help='Unregister a module', nargs=1)
        self.parser.add_argument('-r', '--reload', metavar='MODULE', action='store', dest='reload', default='',\
                      help='Reload a module', nargs=1)
        self.parser.add_argument('-l', '--list', action='store_true', dest='list', default=False,\
                      help='List loaded modules')

    def processCmd(self, oMsg):
        result = ''
        (args, err) = self.getParsedArgs(oMsg.args)

        if err != '':
            result = err
        elif args.register:
            v = ' '.join(args.register)
            oMatrix = CNBMatrix.getInstance()
            result = oMatrix.registerMod(v)
        elif args.unregister:
            v = ' '.join(args.unregister)
            oMatrix = CNBMatrix.getInstance()
            result = oMatrix.unregisterMod(v)
        elif args.reload:     
            v = ' '.join(args.reload)
            oMatrix = CNBMatrix.getInstance()
            oMod = oMatrix.getModule(v)
            if oMod:
                fName = oMod.fileName
                #oMatrix.unregisterMod(fname)
                oMatrix.reloadMod(fName)
                oMatrix.registerMod(fName)
                result = 'Module reloaded'
            else:
                result = 'Failed to reload module'
        elif args.list:
            oMatrix = CNBMatrix.getInstance()
            result = oMatrix.getMods(oMsg)
        elif args.help:
            result = self.getUsage()
        else:
            oMatrix = CNBMatrix.getInstance()
            result = oMatrix.getMods(oMsg)

        return result
