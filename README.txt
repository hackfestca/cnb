============================
The Chuck Norris Bot Project
============================

The Chuck Norris Bot (CNB) project is a multi-protocol chat bot. It currently
support XMPP/Jabber and IRC. 

The concept is that the bot has a single "brain" but connect to multiple
servers at once so beside responding to simple bot tasks such as saying
hello, launching nmap, replying Chuck Norris facts and more, the bot can do
some correlated tasks such as outputing text from an IRC channel to a XMPP room.


Prerequisite
============
The bot depends on the following packages:

* python-irclib 
* python-xmpp 
* python-pywapi 
* python-httplib2 
* python-libxml2 
* python-django
* nmap 


How to use
==========

Setting up the main config file
-------------------------------

First, go to *config/* folder and open the *cnb.conf*. This is the main config
file. Most of this should not have to change, except for the **connectors** and 
**smtp** sections. Here is an example of a *cnb.conf* file. Simply fill the
<...> fields.
    [global]
    version = 0.20
    pid-file = /tmp/cnb.pid
    log-format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
    log-dir = log/cnb/
    pid-dir = pid/
    conf-dir = config/
    class-dir = classes/
    module-dir = classes/modules/
    nickname = Chuck
    
    [connectors]
    auto = [freenode.irc.conf, gmail.xmpp.conf]
    
    [smtp]
    smtp-user = <an email address>
    smtp-pass = <a password>
    smtp-host = <a smtp server>
    smtp-port = <a smtp port>

As you can see in the **connectors** section, there are two more config files. 
These are connection config files containing informations to connect to a chat 
server. The next section explain how to setup a connection config file. 


Setting up a connection config file
-----------------------------------

The bot will import any *\*.conf* files that are in the *config/* folder. Here's
the syntax of an IRC connection file. Again, simply fill the <...> fields. 
    [bot]
    type = irc
    log-file = freenode.irc.log
    username = <an irc username>
    password = <a password>
    server = <an irc server>
    channels = [<a list of chan to connect (Syntax: chan:[password],...)>]
    auto-join = 1
    auto-start = 1
    auto-reconnect = 1
    verbose = 1
    admins = [<a list of admins (Syntax: nick1,...). WARNING: THIS IS NOT SECURE>]

And this is a XMPP connection file
    [bot]
    type = xmpp|xmpp-gtalk  //xmpp for custom xmpp, xmpp-gtalk for gmail chat
    log-file = gmail.xmpp.log
    username = <an email address>
    password = <the email password>
    server = <overwrite only if the server can't be resolved from SRV lookup.
    See <http://tools.ietf.org/html/rfc6120#section-3.2.1> >
    rooms = [<a list of default rooms to join (Syntax: room1,...)>]
    nickname = <a nick name>
    auto-join = 1
    auto-start = 1
    auto-reconnect = 1
    verbose = 1
    admins = [<a list of admins (Syntax: email1,...)>]
    room-admins = [<a list of admins (Syntax: user1,...)>]

Launching the bot
-----------------
It is recommended to start it through a service

#!/usr/bin/env python
To simply run the bot:
    ./ChuckNorrisBot.py [--help]

Run the bot, auto connect and auto join
    ./ChuckNorrisBot.py -j -s

Run the bot as a daemon
    ./ChuckNorrisBot.py -d --pid-file /tmp/ChuckNorrisBot.pid

To run the bot as another user
    ./ChuckNorrisBotService start|stop|restart|status


Bot Security
============

Some principle
--------------

* Never run the bot as root
* For long time use, jail it on a VM
* Set up admin list correctly
    * You don't want anybody to run nmaps from your home?

Hardening the bot
-----------------

TBD
* How to jail?
* How to disable modules?


Contributors
============
This bot was created by Martin Dubé as a Hackfest Project (See:
<http://hackfest.ca>). Martin is still the main collaborator and reviser.

For any comment, questions, insult: martin d0t dube at hackfest d0t com. 

Thanks also to
--------------
Authors and maintainers of the following projects, which make this bot fun and
useful:
* findmyhash
* nmap
* eliza
* Trivia Game (vn at hackfest d0t ca)
* Python
* And every project I forgot


