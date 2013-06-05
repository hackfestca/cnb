#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
CNB Matrix Module - weather
'''

import string
import warnings
from cnb.cnbMatrixModule import CNBMatrixModule

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    try:
        import pywapi
    except ImportError:
        print >> sys.stderr, """
        You need to install pywapi
        On Debian-based systems, install the python-pywapi package.
        """
        sys.exit(-1)

class CNBMMWeather(CNBMatrixModule):
    """

    """

    name = 'weather'
    usage = 'weather'
    desc = 'Print the weather using pywapi'
    aliases = []

    def __init__(self,log):
        CNBMatrixModule.__init__(self,log)

    def __del__(self):
        pass

    def processCmd(self, oMsg):
        city = 'Quebec'
        country = 'CA'
        location = city + ', ' + country
        yahoo_result = pywapi.get_weather_from_yahoo('CAXX0385')

        result = "It is " + string.lower(yahoo_result['condition']['text']) + \
            " and " + yahoo_result['condition']['temp'] + "C now in " + location + "."
        return result

