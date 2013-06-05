============================
The Chuck Norris Bot Project
============================

The Chuck Norris Bot (CNB) project is a multi-protocol chat bot. It currently
supports XMPP/Jabber and IRC. 

The concept is that the bot has a single "brain" but connect to multiple
servers at once so beside responding to simple bot tasks such as saying
hello, launching nmap, replying Chuck Norris facts and more, the bot can do
some correlated tasks such as spying an IRC chan from an XMPP room.


Prerequisite
============
The bot depends on the following packages:

* python-irclib (LGPL v2.0)
* python-xmpp  (GPL v2.0)
* python-pywapi (MIT)
* python-httplib2 (MIT)
* python-libxml2 (MIT)
* python-django (BSD)
* nmap 

The XMPP/Jabber connector was tested on ejabberd and GTalk.
The IRC connector was tested on freenode.net.
The bot was tested on Debian Stable (wheezy atm).

Install
=======

First download the code from git
    git clone https://github.com/hackfestca/cnb cnb

Then run setup.py
    ./cnb/setup.py install

How to use
==========

Setting up the main config file
-------------------------------

First, go to */etc/cnb*/ folder and copy the *cnb.conf.default* to *cnb.conf*. This is the main config
file. Most of this should not be changed, except for the **connectors** and 
**smtp** sections. Here is an example of a *cnb.conf* file. Simply fill the
<...> fields.

    | [global]
    | #root-dir = <string>  (dynamically added)
    | #bin-dir = <string>  (dynamically added)
    | #config-dir = <string> (dynamically added)
    | #log-dir = <string>  (dynamically added)
    | #tp-dir = <string>  (dynamically added)
    | #pid-file = <string>  (dynamically added if started as a daemon)
    | version = 0.20
    | log-format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
 
    | [connectors]
    | auto = [freenode.irc.conf, gmail.xmpp.conf]
 
    | [smtp]
    | smtp-user = <an email address>
    | smtp-pass = <a password>
    | smtp-host = <a smtp server>
    | smtp-port = <a smtp port>

As you can see in the **connectors** section, there are two more config files. 
These files contain all necessary information to connect a chat server.
The next section explain how to setup a connection config file. 


Setting up a connection config file
-----------------------------------

The bot will import files specified in *cnb.conf* file. Here's
the syntax of an IRC connection file. Again, simply fill the <...> fields. 

    | [bot]
    | type = irc
    | log-file = freenode.irc.log
    | username = <an irc username>
    | password = <a password>
    | server = <an irc server>
    | channels = [<a list of chan to connect (Syntax: chan:[password],...)>]
    | auto-join = 1
    | auto-start = 1
    | auto-reconnect = 1
    | verbose = 0
    | admins = [<a list of admins (Syntax: nick1,...). WARNING: THIS IS NOT SECURE>]

And this is a XMPP connection file

    | [bot]
    | #id = <int> (dynamically added)
    | #config-file = <string> (dynamically added)
    | #monday-suck-room = <string> (dynamically added)
    | type = xmpp|xmpp-gtalk  //xmpp for custom xmpp, xmpp-gtalk for gmail chat
    | log-file = gmail.xmpp.log
    | username = <insert username here>
    | password = <insert password here>
    | server = <overwrite only if the server can't be resolved from SRV lookup.
    | See <http://tools.ietf.org/html/rfc6120#section-3.2.1> >
    | rooms = [<a list of default rooms to join (Syntax: room1,...)>]
    | nickname = <insert nick name here>
    | auto-join = 1
    | auto-start = 1
    | auto-reconnect = 1
    | verbose = 0
    | admins = [<a list of admins (Syntax: email1,...)>]
    |
    | muc-domain = <insert muc domain here>


Running the bot
-----------------

It is recommended to start it as a shell script first to see any errors
and then start it as a service

To run the bot as a shell script:

    [/usr/local/bin/]cnb-cli [--help]

To run as a service:

    sudo /etc/init.d/cnb start|stop|restart|status


Bot Security
============

Some principle
--------------

* Never run the bot as root
* For long time use, jail it on a VM
* Set up admin list correctly
    * You don't want anybody to run nmaps from your home?


Bot Hardening
-----------------

By default, running Chuck as a service will run it as the user "cnb". It 
is always a good idea to run the bot as a user with limited privileges.

Disabling modules can also reduce attack vectors. Disable modules by removing 
symbolic links in the cnb/modEnabled folder (apache style).


Docs
====

If you are interested to know more about the code, the documentation is in 
*docs/* folder, generated with epydoc.

It is also accessible here: http://htmlpreview.github.io/?https://github.com/hackfestca/cnb/blob/master/docs/index.html


Contributors
============
This bot was created by Martin Dubé as a Hackfest Project (See:
http://hackfest.ca). Martin is not a developper but still the main collaborator and reviser.
Furthermore, a lot of ideas came from Hackfest crew and community.

For any comment, questions, insult: martin d0t dube at hackfest d0t com. 

Thanks also to
--------------
Authors and maintainers of the following projects, which make this bot fun and
useful:

* findmyhash
* Urban Dictionary
* nmap
* Trivia Game (vn at hackfest d0t ca)
* Python
* And every project I forgot


