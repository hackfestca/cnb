#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This is the config class of CNB. 
'''

import os
import sys
import ConfigParser
from singleton import Singleton

@Singleton
class CNBConfig(ConfigParser.RawConfigParser):
    """
    In addition to inherit from RawConfigParser, it is a singleton so it can be instanciated once. 
    """

    sConfigFolder = 'config'
    """
    @ivar: Config folder name
    @type: string
    """

    sMainConfigFile = 'cnb.conf'
    """
    @ivar: Main config file. The file contains global configuration informations. 
    @type: string
    """

    def __init__(self):
        ConfigParser.RawConfigParser.__init__(self)

    def __del__(self):
        pass

    def _normalize(self):
        """
        This method let you import arrays from config files. The syntax must be: "var: ['value1','value2','...']". 
        """
        for s in self.sections():
            for (n,v) in self.items(s):
                if len(v) > 0:
                    if v[0] == '[' and v[len(v)-1] == ']':
                        nv = self._striplist((v[1:-1]).split(','))
                    else:
                        nv = v.strip()
                    self.set(s,n,nv)
                else:
                    self.set(s,n,v)

    def _striplist(self,l):
        """
        This method strip a list
        """
        return([x.strip() for x in l])

    def setPath(self,path):
        """
        This method let you overwrite the config folder path
        @param path: The path to the config files.
        @type path: string
        """
        self.sConfigFolder = path

    def loadMain(self):
        """
        This method load the main config file (cnb.conf)
        """
        self.load(self.sConfigFolder + self.sMainConfigFile)
        self._normalize()

    def load(self,sFile):
        """
        This method load a specific file
        @param sFile: The path to the config file.
        @type sFile: string
        """
        try:
            self.readfp(open(sFile))
        except Exception, e:
            print 'Could not open main config file at "' + sFile + '"'
            print e
            sys.exit(1)

    def overwriteFromArgs(self, options):
        """
        This method overwrite some "config values" from user inputs.
        @param options: A option object containing values to import.
        @type options: OptionParser
        """
        if options.version:
            print 'Version: ' + self.get('global', 'version')
            sys.exit(0)
           
        if options.daemon:
            options.autostart = True
            options.autojoin = True
            print 'Overwriting self.daemon = ' + str(options.daemon)
            self.set('global', 'daemon', True)
        else:
            self.set('global', 'daemon', False)

        
        if options.pidfile:
            print 'Overwriting self.pid-file = ' + str(options.pidfile)
            self.set('global', 'pid-file', str(options.pidfile))
            pid = str(os.getpid())
            file(self.get('global', 'pid-file'),'w+').write("%s\n" % pid)
    
