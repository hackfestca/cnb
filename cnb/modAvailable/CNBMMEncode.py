#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - encode
'''

import string
import urllib
import base64
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMEncode(CNBMatrixModule):
    """

    """

    name = 'encode'
    usage = ''
    desc = 'Encode a string using different algorithm'
    aliases = []
    isAdmin = False


    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)
        self._initOptParser()

    def _initOptParser(self):
        CNBMatrixModule._initOptParser(self,False)

        encodeGrp = self.parser.add_argument_group('Encoding Options')
        decodeGrp = self.parser.add_argument_group('Decoding Options')

        encodeGrp.add_argument('--rot13', action='store_true', dest='rot13', default=False,\
                      help='Encode in rot13')
        encodeGrp.add_argument('--rotn', action='store_true', dest='rotn', default=False,\
                      help='Encode in rotN (need to specify -n [0-26])')
        encodeGrp.add_argument('--rotall', action='store_true', dest='rotall', default=False,\
                      help='Encode in all possible rotN (multiple output)')

        encodeGrp.add_argument('--b64', action='store_true', dest='b64', default=False,\
                      help='Encode in base64')
        encodeGrp.add_argument('--morse', action='store_true', dest='morse', default=False,\
                      help='Encode in morse')
        encodeGrp.add_argument('--url', action='store_true', dest='url', default=False,\
                      help='Encode in URL')

        decodeGrp.add_argument('--ub64', action='store_true', dest='ub64', default=False,\
                      help='Decode string from base64')
        decodeGrp.add_argument('--umorse', action='store_true', dest='umorse', default=False,\
                      help='Decode string from morse')
        decodeGrp.add_argument('--uurl', action='store_true', dest='uurl', default=False,\
                      help='Decode string from URL')

        self.parser.add_argument("-h", "--help", action="store_true", dest='help', default=False,\
                      help='Display help')
        self.parser.add_argument("-n", action="store", dest='n', type=int, default=0,\
                      help='Set a rotation iterator (for --rotn only)', nargs=1)
        self.parser.add_argument('string', metavar='STRING', action='store', default='',\
                      help='Text to encode or Cipher to decode', nargs='*')

    def _rotN(self, s, n):
        lc = string.lowercase
        trans = string.maketrans(lc, lc[n:] + lc[:n])
        return string.translate(s, trans)

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
        elif args.rot13:
            if s != '':
                result = s.encode('rot13')
        elif args.rotn:
            if s != '' and args.n >= 0:
                result = self._rotN(s,args.n)   
        elif args.rotall:
            if s != '':
                result = ''
                for i in range(1,26):
                    result = result + self._rotN(s,i) + "\n"
        elif args.b64:
            if s != '':
                result = base64.b64encode(s)
        elif args.morse:
            if s != '':
                result = MorseEncoder().encode(s)
        elif args.url:
            if s != '':
                result = urllib.quote(s)

        elif args.ub64:
            if s != '':
                result = base64.b64decode(s)
        elif args.umorse:
            if s != '':
                result = MorseEncoder().decode(s)
        elif args.uurl:
            if s != '':
                result = urllib.unquote(s)
            
        elif args.help:
            result = self.getUsage()
        else:
            result = self.getUsage()

        return result

class MorseEncoder():
    morseAlphabet ={
        "A" : ".-",
        "B" : "-...",
        "C" : "-.-.",
        "D" : "-..",
        "E" : ".",
        "F" : "..-.",
        "G" : "--.",
        "H" : "....",
        "I" : "..",
        "J" : ".---",
        "K" : "-.-",
        "L" : ".-..",
        "M" : "--",
        "N" : "-.",
        "O" : "---",
        "P" : ".--.",
        "Q" : "--.-",
        "R" : ".-.",
        "S" : "...",
        "T" : "-",
        "U" : "..-",
        "V" : "...-",
        "W" : ".--",
        "X" : "-..-",
        "Y" : "-.--",
        "Z" : "--..",
        " " : "/",
        "." : "/"
        }

    def __init__(self):
        self.inverseMorseAlphabet = dict((v,k) for (k,v) in self.morseAlphabet.items())

    def decode(self, code, positionInString = 0):
        """
        parse a morse code string positionInString is the starting point for decoding
        """
        
        if positionInString < len(code):
            morseLetter = ""
            for key,char in enumerate(code[positionInString:]):
                if char == " ":
                    positionInString = key + positionInString + 1
                    letter = self.inverseMorseAlphabet[morseLetter]
                    return letter + self.decode(code, positionInString)
                
                else:
                    morseLetter += char
        else:
            return ""
        
    def encode(self,message):
        """
        encode a message in morse code, spaces between words are represented by '/'
        """
        encodedMessage = ""
        for char in message[:]:
            if char.upper() in self.morseAlphabet:
                encodedMessage += self.morseAlphabet[char.upper()] + " "
                
        return encodedMessage
