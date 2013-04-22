#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - chuckkukdo
'''

# System imports
from cnb.cnbMatrixModule import CNBMatrixModule

class CNBMMChuckKukDo(CNBMatrixModule):
    """

    """

    name = 'chuckkukdo'
    usage = 'chuckkukdo'
    desc = 'Print the Chuck Kuk Do (http://en.wikipedia.org/wiki/Chun_Kuk_Do)'
    aliases = []
    

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        result = " \n \
	1- I will develop myself to the maximum of my potential in all ways.\n \
	2- I will forget the mistakes of the past and press on to greater achievements.\n \
	3- I will continually work at developing love, happiness and loyalty in my family.\n \
	4- I will look for the good in all people and make them feel worthwhile.\n \
	5- If I have nothing good to say about a person, I will say nothing.\n \
	6- I will always be as enthusiastic about the success of others as I am about my own.\n \
	7- I will maintain an attitude of open-mindedness.\n \
	8- I will maintain respect for those in authority and demonstrate this respect at all times.\n \
	9- I will always remain loyal to my God, my country, family and my friends.\n \
	10- I will remain highly goal-oriented throughout my life because that positive attitude helps my family, my country and myself.\n \
        "
        return result

