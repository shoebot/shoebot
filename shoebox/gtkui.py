'''
Experimental GTK front-end for Shoebox

- implements the gobject-based socket server from
  http://roscidus.com/desktop/node/413
'''

import sys, gtk, random, StringIO
import shoebox
import gobject, socket
from pprint import pprint

class ShoeboxCanvas(gtk.DrawingArea):
    def __init__(self, inputfilename):
        super(ShoeboxCanvas, self).__init__()
        self.connect("expose_event", self.expose)
        
        self.infile = inputfilename
        self.box = shoebox.Box()
        self.box.run(self.infile)
    
    def expose(self, widget, event):
        '''Handle expose events.'''
        # reset context
        self.context = None
        self.context = widget.window.cairo_create()
        # set a clip region for the expose event
        self.context.rectangle(event.area.x, event.area.y,
                            event.area.width, event.area.height)
        self.context.clip()
        
        # attach box to context
        self.box.setsurface(target=self.context)
        # run the input script              

#        pprint(self.box.namespace['variables']) 
        self.draw()	
        return False
    
    def redraw(self,dummy='moo'):
        '''Handle redraws.'''
        self.queue_draw()
    
    def draw(self):
        self.box.namespace['setup']()
        self.box.namespace['draw']()
        

class MainWindow:
    def __init__(self,filename):
        self.canvas = ShoeboxCanvas(filename)

    def run(self):
        '''Setup the main GTK window.'''
        window = gtk.Window()
        window.connect("destroy", gtk.main_quit)
        self.canvas.set_size_request(1024, 768)
        window.add(self.canvas)
        window.show_all()
        
        gtk.main()

# ---- SOCKET SERVER ----
    def server(self, host, port):
        '''Initialize server and start listening.'''
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(1)
        print "Listening..."
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
            ## FIXME
            # this statement is bottlenecking the whole thing
            if len(incoming.split()) == 2:
                var, value = incoming.split()
                # is value in our variables list?
                if var in self.canvas.box.namespace:
                    # set the box namespace to the new value
                    print "VALUE CHANGED"
                    print self.canvas.box.namespace[var]
                    ## HACKING HERE, commented doesn't work but would be desirable
#                    self.canvas.box.namespace[var] = value.strip(';')
                    self.canvas.box.namespace[var] = float(value.strip(';'))
                    print self.canvas.box.namespace[var]
                    # and redraw
                    self.canvas.redraw()
                return True
            else:
                return True
                
# --------

if __name__ == "__main__":
    import sys
    win = MainWindow('letter_h_obj.py')
    win.server('',7777)
    win.run()
