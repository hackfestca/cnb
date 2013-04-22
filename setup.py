#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup,Command
from distutils.command.install import install
import os
import sys
import crypt
import random
import string

if not os.geteuid()==0:
    sys.exit("\nOnly root can run this script\n")

class cnbInstall(install):
    def run(self):
        install.run(self)

        insDep = raw_input("Chuck need some dependencies such as python-xmpp, python-irclib, nmap and lynx. Some module might not work without these dependencies. Do you want the install script to attempt an aptitude install? [yN]")
        if insDep == 'y' or insDep == 'Y':
            print 'Running: "aptitude install python-irclib python-xmpp nmap python-pywapi python-xmpp python-httplib2 python-libxml2 python-django lynx"'
            os.system('aptitude install python-irclib python-xmpp nmap python-pywapi python-xmpp python-httplib2 python-libxml2 python-django lynx')

        print 'Generating password for cnb account'
        p = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(100))
        s = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
    
        print 'Creating cnb account'
        os.system("useradd -p `mkpasswd -m SHA-512 "+p+" "+s+"` cnb")
   
        print 'Setting ownership: "chown -R cnb:cnb /etc/cnb"' 
        os.system('chown -R cnb:cnb /etc/cnb')

        print 'Setting security: "chmod 0750 /etc/cnb"'
        os.system('chmod 0750 /etc/cnb')

        print 'Setting security: "chmod 0640 /etc/cnb/*"'
        os.system('chmod 0640 /etc/cnb/*')

        print 'Setting security: "chmod 0750 /etc/cnb/facts"'
        os.system('chmod 0750 /etc/cnb/facts')

        print 'Setting security: "chmod 0640 /etc/cnb/facts/*"'
        os.system('chmod 0640 /etc/cnb/facts/*')

        print 'Setting security: "chmod 0750 /etc/cnb/trivia"'
        os.system('chmod 0750 /etc/cnb/trivia')

        print 'Setting security: "chmod 0640 /etc/cnb/trivia/*"'
        os.system('chmod 0640 /etc/cnb/trivia/*')
        
        print 'Setting ownership: "chown cnb:cnb /etc/init.d/cnb"' 
        os.system('chown cnb:cnb /etc/init.d/cnb')

        print 'Setting security: "chmod 0640 /etc/init.d/cnb"'
        os.system('chmod 0750 /etc/init.d/cnb')

        print 'Setting ownership: "chown -R cnb:cnb /usr/local/cnb"'
        os.system('chown -R cnb:cnb /usr/local/cnb')

        print 'Setting ownership: "chown cnb:cnb /var/log/cnb"'
        os.system('chown -R cnb:cnb /var/log/cnb')

        print 'Setting security: "chmod 0750 /var/log/cnb"'
        os.system('chmod 0750 /var/log/cnb')

        print 'Setting security: "chmod 0750 /var/log/cnb/findmyhash"'
        os.system('chmod 0750 /var/log/cnb/findmyhash')

        print 'Setting security: "chmod 0750 /var/log/cnb/nmap"'
        os.system('chmod 0750 /var/log/cnb/nmap')

class cnbUninstall(Command):
    description = 'Uninstall the project from the system (was tested on Debian Squeeze only)'
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd

        print 'Deleting /etc/cnb/*.default'
        os.system('rm -rf /etc/cnb/*.default')

        print 'Deleting /etc/cnb/facts'
        os.system('rm -r /etc/cnb/facts')

        print 'Deleting /etc/cnb/trivia'
        os.system('rm -r /etc/cnb/trivia')

        print 'Deleting /etc/init.d/cnb'
        os.system('rm /etc/init.d/cnb')

        print 'Deleting /usr/local/bin/cnb-cli'
        os.system('rm /usr/local/bin/cnb-cli')

        print 'Deleting /usr/local/cnb'
        os.system('rm -rf /usr/local/cnb/')
        
        print 'Deleting /usr/local/lib/python2.6/dist-packages/cnb'
        os.system('rm -rf /usr/local/lib/python2.6/dist-packages/cnb/')

        print 'Deleting /var/run/cnb'
        os.system('rm -rf /var/run/cnb/')
        
        print 'Deleting /var/log/cnb'
        os.system('rm -rf /var/log/cnb/')
        
        print 'Deleting cnb account'
        os.system('deluser cnb')

setup(
    name='HFChuckNorrisBot',
    version='0.1.123',
    author='Martin Dubé',
    author_email='martin.dube@hackfest.com',
    url='https://github.com/hackfestca/cnb',
    license='LICENSE.txt',
    description='Hackfest Chuck Norris XMPP/Jabber and IRC Bot',
    long_description=open('README.txt').read(),
    keywords = ('bot', 'xmpp', 'jabber', 'irc', 'hackfest'),
    classifiers=['Development Status :: 3 - Alpha',\
                 'Environment :: Console',\
                 'Environment :: No Input/Output (Daemon)',\
                 'Intended Audience :: Developers',\
                 'Intended Audience :: Information Technology',\
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',\
                 'Natural Language :: English',\
                 'Natural Language :: French',\
                 'Operating System :: POSIX :: Linux',\
                 'Programming Language :: Python :: 2.6',\
                 'Topic :: Communications :: Chat',\
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',\
                 'Topic :: Utilities'],
    packages=['cnb',\
             'cnb.test',\
             'cnb.modAvailable',\
             'cnb.modEnabled'],
    package_dir = { '': '.' },
    package_data={'': ['docs/*']},
    scripts=['bin/cnb-cli'],
    data_files=[('/etc/cnb', ['config/cnb.conf.default', 'config/freenode.irc.conf.default', 'config/gmail.xmpp.conf.default']),\
                ('/etc/cnb/facts', ['facts/facts.en.txt', 'facts/facts.fr.txt', 'facts/facts.pr0n.txt', 'facts/tamere.txt']),\
                ('/etc/cnb/trivia', ['facts/questions.txt', 'facts/trivia.hf2k12.txt']),\
                ('/etc/init.d', ['bin/init/cnb']),\
                ('cnb/thirdParties', ['thirdParties/findmyhash/findmyhash_v1.1.2.py', 'thirdParties/gtranslate/gtranslate.py']),\
                ('cnb/scripts', ['bin/misc/compile.en.sh', 'bin/misc/compile.fr.sh', 'bin/misc/gendoc.sh', 'bin/misc/inst-dep.sh']),\
                ('/var/log/cnb', []),\
                ('/var/log/cnb/findmyhash', []),\
                ('/var/log/cnb/nmap', [])],
    requires=[
        "irclib (>=0.4.8)",
        "xmpp (>=0.4.1)",
        "pywapi (>=0.2.2)",
        "httplib2 (>=0.6.0)",
        "libxml2 (>=2.7.8)",
        "django (>=1.2.3)",
    ],
     cmdclass={
        'install': cnbInstall,
        'uninstall': cnbUninstall 
    }
)
