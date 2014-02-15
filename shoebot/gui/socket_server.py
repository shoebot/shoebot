'''
gobject-based socket server from
http://roscidus.com/desktop/node/413
'''
import sys
import gobject, socket
import gettext, locale
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

class SocketServerMixin(object):
    def server(self, host, port):
        '''Initialize server and start listening.'''
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(1)
        print _("Listening on port %i...") % (port)
        gobject.io_add_watch(self.sock, gobject.IO_IN, self.listener)

    def listener(self, sock, *args):
        '''Asynchronous connection listener. Starts a handler for each connection.'''
        self.conn, self.addr = self.sock.accept()
        print _("Connected")
        gobject.io_add_watch(self.conn, gobject.IO_IN, self.handler)
        self.conn.send(self.msg_banner())
        return True

    def msg_banner(self):
        return BANNER

    def msg_var_value(self, name):
        variable = self.bot._vars[name]
        return 'bot: {}={}\n'.format(name, variable.sanitize(variable.value))

    def msg_bye(self):
        return "See you next time.\n"

    def msg_dir(self):
        # Show variables
        d = self.bot._vars
        return '{}\n'.format('\n'.join(['%s = %s' % (key, var.value) for (key, var) in d.items()]))

    def handler(self, conn, *args):
        '''Asynchronous connection handler. Processes each line from the socket.'''
        line = conn.recv(4096)
        if not len(line):
            print _("Connection closed.")
            return False
        else:
            incoming = line.strip().split('\n')
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

