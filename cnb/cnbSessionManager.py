#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Chuck Norris Bot - Session Manager
'''

from cnbMatrix import CNBMatrix
from singleton import Singleton

@Singleton
class CNBSessionManager():
    """
    Not implemented yet
    The idea is to stock information about a user, exactly like a session, so we can make time based event.
    Example: Generate special behavior based on what the user is and has done
    Example: If the bot detect that a user is french, the default use of .fact could output french quotes. In this case, The module would have to interact with CNBSessionManager before replying.
    @todo: Determine which database to use if a necessity
    """

    def __init__(self):
        pass
