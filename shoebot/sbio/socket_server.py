"""
gobject-based socket server from
http://roscidus.com/desktop/node/413

Handles interaction when connecting over a socket, e.g. telnet.
The actual handling of commands is passed to te shell module.

$ sbot -ws examples/basic/vars_boolean.bot &
$ telnet 127.0.0.1 7777

# Now enter the commands below and see the bot state change
color_switch=False
color_switch=True
"""

import locale
import sys
import socket
import gettext

from shoebot.core.backend import gi

from gi.repository import GObject
from shell import ShoebotCmd

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext


# For now this is a bit basic, but works enough.


BANNER = """
############`             [Welcome to Shoebot Telnet Console.]`
##```####```              `````````````````````````````````````
############`
############`
##```````````
############`
`````````````

Set variables with  var=value

Enter vars to view variables.
Enter bye or press CTRL-D to quit.

"""

INTRO = "[o_o] " + '"Shoebot Telnet Shell, enter "help" for help."'

def create_listening_socket(host, port, handler):
    """
    Create socket and set listening options
    :param host:
    :param port:
    :param handler:
    :return:
    """
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((host, port))
    sock.listen(1)

    GObject.io_add_watch(sock, GObject.IO_IN, handler)
    return sock

class SocketServer(object):
    def __init__(self, bot, host, port):
        '''Initialize server and start listening.'''
        create_listening_socket(host, port, self.listener)
        self.shell = None
        self.bot = bot

    def listener(self, sock, *args):
        '''Asynchronous connection listener. Starts a handler for each connection.'''
        conn, addr = sock.accept()
        f = conn.makefile(conn)
        self.shell = ShoebotCmd(self.bot, stdin=f, stdout=f, intro=INTRO)

        print(_("Connected"))
        GObject.io_add_watch(conn, GObject.IO_IN, self.handler)
        if self.shell.intro:
            self.shell.stdout.write(str(self.shell.intro)+"\n")
            self.shell.stdout.flush()
        return True

    def handler(self, conn, *args):
        '''
        Asynchronous connection handler. Processes each line from the socket.
        '''
        # lines from cmd.Cmd
        self.shell.stdout.write(self.shell.prompt)
        line = self.shell.stdin.readline()
        if not len(line):
            line = 'EOF'
            return False
        else:
            line = line.rstrip('\r\n')
            line = self.shell.precmd(line)
            stop = self.shell.onecmd(line)
            stop = self.shell.postcmd(stop, line)
            self.shell.stdout.flush()
            self.shell.postloop()
            # end lines from cmd.Cmd
            if stop:
                self.shell = None
                conn.close()
            return not stop
