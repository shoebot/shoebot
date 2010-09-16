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
        return True

    def handler(self, conn, *args):
        '''Asynchronous connection handler. Processes each line from the socket.'''
        line = self.conn.recv(4096)
        if not len(line):
            print _("Connection closed.")
            return False
        else:
            incoming = line.strip().split('\n')
            for packet in incoming:
                var, value = packet.split()
                # is value in our variables list?
                if var in self.bot._namespace:
                    ## TODO: we're forced to convert input to floats
                    # would be a lot nicer to have a check for the var type
                    # self.drawingarea.bot._namespace[var] = value.strip(';')
                    self.bot._namespace[var] = float(value.strip(';'))
                return True
            else:
                return True

