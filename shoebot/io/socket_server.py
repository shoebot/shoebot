'''
gobject-based socket server from
http://roscidus.com/desktop/node/413
'''

import sys
import socket
import gettext, locale

try:
    import gi
except ImportError:
    import pgi
    pgi.install_as_gi()

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

Enter dir() to view variables.
Enter bye() or press CTRL-D to quit.

"""

INTRO = "[o_o] " + '"Shoebot Telnet Shell, enter "help" for help."'


class SocketServer(object):
    def __init__(self, bot, host, port):
        '''Initialize server and start listening.'''
        self.sock = sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((host, port))
        sock.listen(1)

        self.shell = None
        self.bot = bot
        print _("Listening on port %i..." % port)
        GObject.io_add_watch(sock, GObject.IO_IN, self.listener)

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

    #def msg_banner(self):
    #    return BANNER

    # def msg_var_value(self, name):
    #     variable = self.bot._vars[name]
    #     return 'bot: {}={}\n'.format(name, variable.sanitize(variable.value))

    #def msg_bye(self):
    #    return "See you next time.\n"

    #def msg_dir(self):
    #    # Show variables
    #    d = self.bot._vars
    #    return '{}\n'.format('\n'.join(['%s = %s' % (key, var.value) for (key, var) in d.items()]))

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
            return not stop

    def x(self):
        ### TODO - Move setting variables to shell
        incoming = None
        if True:


            for packet in incoming:
                if not packet or packet.startswith('#'):
                    continue
                elif packet=='dir()':
                    conn.send(self.msg_dir())
                elif packet in ['\x03', '\x04'] or packet.lower() in ['bye', 'quit', 'bye()', 'quit()']:
                    conn.send(self.msg_bye())
                    conn.close()
                    return False
                elif '=' in packet:
                    name, value = [part.strip() for part in packet.split('=')]
                    # is value in our variables list?
                    if name in self.bot._vars:
                        ## TODO: we're forced to convert input to floats
                        # would be a lot nicer to have a check for the var type
                        # self.drawingarea.bot._namespace[var] = value.strip(';')
                        #value = float(value.strip(';'))
                        variable = self.bot._vars[name]
                        variable.value = variable.sanitize(value.strip(';'))

                        success, msg = self.var_changed(name, variable.value)
                        if success:
                            conn.send(self.msg_var_value(name))
                        else:
                            conn.send('{}\n'.format(msg))
                    else:
                        conn.send('Error: Unknown variable: {}\n'.format(name))
                elif packet in self.bot._vars:
                    conn.send(self.msg_var_value(packet))
                else:
                    conn.send('Error: Unknown command: {}\n'.format(packet))
            return True

