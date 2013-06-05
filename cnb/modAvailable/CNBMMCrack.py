#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - crack
'''

import subprocess
from copy import copy
from time import sleep, strftime
from cnb.cnbManager import CNBManager
from cnb.cnbConfig import CNBConfig
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMCrack(CNBMatrixModule):
    """ 
    @todo: Crack using a huge dictionnary
    @todo: Cache cracked passwords
    """

    name = 'crack'
    usage = 'crack [TYPE] HASH1 [HASH2 ...]'
    desc = '''The bot uses bozocrack to google some hash.
            MD4       - RFC 1320
            MD5       - RFC 1321
            SHA1      - RFC 3174 (FIPS 180-3)
            SHA224    - RFC 3874 (FIPS 180-3)
            SHA256    - FIPS 180-3
            SHA384    - FIPS 180-3
            SHA512    - FIPS 180-3
            RMD160    - RFC 2857
            GOST      - RFC 5831
            WHIRLPOOL - ISO/IEC 10118-3:2004
            LM        - Microsoft Windows hash
            NTLM      - Microsoft Windows hash
            MYSQL     - MySQL 3, 4, 5 hash
            CISCO7    - Cisco IOS type 7 encrypted passwords
            JUNIPER   - Juniper Networks $9$ encrypted passwords
            LDAP_MD5  - MD5 Base64 encoded
            LDAP_SHA1 - SHA1 Base64 encoded
'''
    aliases = []

    FIND_MY_HASH_FILE = 'findmyhash/hashlist'
    FIND_MY_HASH_CMD = ['findmyhash_v1.1.2.py', '-f']
    MSG_CRACKING = 'On my way...'
    MSG_CRACKED = '***** HASH CRACKED!! *****'

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = ''
        if len(oMsg.args) > 1:
            hashType = oMsg.args[0].upper()
            stringList = oMsg.args[1::]
            
            # Create temporary file
            oConfig = CNBConfig.getInstance()
            sLogDir = oConfig.get('global', 'log-dir')
            tmpFileName = sLogDir + self.FIND_MY_HASH_FILE + strftime("%Y-%m-%d_%H%M%S") + '.txt'
            if len(stringList) > 1:
                fh = open(tmpFileName,"w")
                for h in stringList:
                    fh.write(h + "\n")
                fh.close()
            else:
                fh = open(tmpFileName,"w")
                fh.write(stringList[0] + "\n")
                fh.close()
                
            sTpDir = oConfig.get('global', 'tp-dir')
            cmd = copy(self.FIND_MY_HASH_CMD)
            cmd[0] = sTpDir + cmd[0]
            cmd.insert(1, hashType)
            cmd.append(tmpFileName)
            self.log.info(str(cmd))

            # Telling the user that the hash will be cracked
            oConMgr = CNBManager.getInstance()
            oConMgr.sayCNB(oMsg.conId,oMsg.getSource(),self.MSG_CRACKING)

            # Process and reply
            result = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

            # If the pass was cracked, remove some crap before sending results
            if self.MSG_CRACKED in result:
                result = result[result.find(self.MSG_CRACKED)::]
                fh = open(tmpFileName,"a")
                fh.write(result + "\n")
                fh.close()
        else:
            result = "This cmd takes at least 2 arguments, check help"
        return result
