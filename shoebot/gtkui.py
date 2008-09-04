'''
Experimental GTK front-end for Shoebot

implements the gobject-based socket server from
http://roscidus.com/desktop/node/413
'''

import sys, gtk, random, StringIO
import shoebot
import cairo
import gobject, socket
from pprint import pprint

class ShoebotCanvas(gtk.DrawingArea):
    def __init__(self, mainwindow, box = None):
        super(ShoebotCanvas, self).__init__()
        self.connect("expose_event", self.expose)
        # get the box object to display
        self.box = box

        # make a dummy surface and context, otherwise scripts without draw()
        # and/or setup() will bork badly
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1,1)
        self.box.setsurface(target=surface)
        self.box.run()

        # set the window size to the one specified in the script
        self.set_size_request(self.box.WIDTH, self.box.HEIGHT)

    def expose(self, widget, event):
        '''Handle GTK expose events.'''

        # reset context
        self.context = None
        self.context = widget.window.cairo_create()
        # set a clip region for the expose event
        self.context.rectangle(event.area.x, event.area.y,
                            event.area.width, event.area.height)
        self.context.clip()

        # attach box to context
        self.box.setsurface(target=self.context)
        if 'setup' in self.box.namespace:
            self.box.namespace['setup']()
        if 'draw' in self.box.namespace:
            self.draw()

        # no setup() or draw() means we have to run the script on each step
        if not 'setup' in self.box.namespace and not 'setup' in self.box.namespace:
            self.box.run()

##        self.draw()
        return False

    def redraw(self,dummy='moo'):
        '''Handle redraws.'''
        # dummy is in the arguments because GTK seems to require it, but works
        # fine with any value, so we get away with this hack
        self.queue_draw()

    def draw(self):
        if 'draw' in self.box.namespace:
            self.box.namespace['draw']()

# additional functions for MainWindow
class SocketServerMixin:
    def server(self, host, port):
        '''Initialize server and start listening.'''
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(1)
        print "Listening on port %i..." % (port)
        gobject.io_add_watch(self.sock, gobject.IO_IN, self.listener)

    def listener(self, sock, *args):
        '''Asynchronous connection listener. Starts a handler for each connection.'''
        self.conn, self.addr = self.sock.accept()
        print "Connected"
        gobject.io_add_watch(self.conn, gobject.IO_IN, self.handler)
        return True

    def handler(self, conn, *args):
        '''Asynchronous connection handler. Processes each line from the socket.'''
        line = self.conn.recv(4096)
        if not len(line):
            print "Connection closed."
            return False
        else:
            incoming = line.strip()
            if len(incoming.split()) == 2:
                var, value = incoming.split()
                # is value in our variables list?
                if var in self.canvas.box.namespace:
                    # set the box namespace to the new value

                    ## TODO: we're forced to convert input to floats
                    # self.canvas.box.namespace[var] = value.strip(';')
                    self.canvas.box.namespace[var] = float(value.strip(';'))
                    # and redraw
                    self.canvas.redraw()
                return True
            else:
                return True

    def __del__(self):


class ShoebotWindow(SocketServerMixin):
    def __init__(self, code=None):
        box = shoebot.Box(gtkmode=True, inputscript=code)
        self.canvas = ShoebotCanvas(self, box)

    def run(self):
        '''Setup the main GTK window.'''
        window = gtk.Window()
        window.connect("destroy", gtk.main_quit)
        window.add(self.canvas)
        window.show_all()

        gtk.main()


##if __name__ == "__main__":
##    import sys
##    win = MainWindow('letter_h_obj.py')
##    win.server('',7777)
##    win.run()
