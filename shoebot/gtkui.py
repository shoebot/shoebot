'''
Experimental GTK front-end for Shoebot

implements the gobject-based socket server from
http://roscidus.com/desktop/node/413
'''

from __future__ import division
import sys, gtk, random, StringIO
import shoebot
from data import Transform
import cairo
import gobject, socket

if sys.platform != 'win32':
    ICON_FILE = '/usr/share/shoebot/icon.png'
else:
    import os.path
    ICON_FILE = os.path.join(sys.prefix, 'share', 'shoebot', 'icon.png')

class ShoebotDrawingArea(gtk.DrawingArea):
    def __init__(self, mainwindow, bot = None):
        super(ShoebotDrawingArea, self).__init__()
        self.mainwindow = mainwindow
        #default dimensions
        width, height = 200,200
        self.is_dynamic = None
        self.connect("expose_event", self.expose)
        # get the bot object to display
        self.bot = bot

        script = self.bot.inputscript
        # check if the script is a file or a string
        import os.path
        if os.path.exists(script):
            lines = open(script, 'r').readlines()
        else:
            lines = script.splitlines()

        # make a dummy surface and context, otherwise scripts without draw()
        # and/or setup() will bork badly
        #
        # the surface will be set in expose()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1,1)
        self.bot.canvas.setsurface(target=surface)

        # check inputscript for size and whether is a static script or not
        # it is not perfect, but should do for the moment
        for line in lines:
            line = line.strip()
            if "size" in line:
                size_line = line.split(";")
                for l in size_line:
                    import re
                    l = re.sub("\s", "", l)
                    if l.startswith("size("):
                        l = l[4:].strip().strip('()')
                        width,height = int(l.split(',')[0]),int(l.split(',')[1])
            elif ("def setup" in line) or ("def draw" in line):
                self.is_dynamic = True

        if self.is_dynamic:
            self.bot.run()
            if 'setup' in self.bot.namespace:
                self.bot.namespace['setup']()

        # set the window size to the one specified in the script
        # self.set_size_request(self.bot.WIDTH, self.bot.HEIGHT)
        self.set_size_request(width, height)

        # RIGHT CLICK HANDLING
        self.menu = gtk.Menu()
        self.menu.attach(gtk.MenuItem('Hello'), 0, 1, 0, 1)

        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)

        self.connect('button_press_event', self.on_button_press)

    def on_button_press(self, widget, event):
        # check for right mouse clicks
        if event.button == 3:
            menu = self.mainwindow.uimanager.get_widget('/Save as')
            menu.popup(None, None, None, event.button, event.time)
            return True
        return False

    def expose(self, widget, event):
        '''Handle GTK expose events.'''

        # reset context
        self.context = None
        self.context = widget.window.cairo_create()
        # set a clip region for the expose event
        self.context.rectangle(event.area.x, event.area.y,
                            event.area.width, event.area.height)
        self.context.clip()
        # clear canvas contents
        self.bot.canvas.clear()
        # reset transforms
        self.bot._transform = Transform()
        # attach bot to context
        self.bot.canvas.setsurface(target=self.context)
##        if 'setup' in self.bot.namespace:
##            self.bot.namespace['setup']()
        if 'draw' in self.bot.namespace:
            self.draw()
        self.bot.canvas.draw()

        # no setup() or draw() means we have to run the script on each step
        if not 'setup' in self.bot.namespace and not 'draw' in self.bot.namespace:
            self.bot.run()
            self.bot.canvas.draw()

##        self.draw()
        return False

    def redraw(self,dummy='moo'):
        '''Handle redraws.'''
        # dummy is in the arguments because GTK seems to require it, but works
        # fine with any value, so we get away with this hack
        self.queue_draw()

    def draw(self):
        if 'draw' in self.bot.namespace:
            self.bot.namespace['draw']()

    def save_output(self, action):
        '''Save the current image to a file.'''
        # action is the menu action pointing the extension to use
        extension = action.get_name()
        filename = 'output.' + extension
        self.bot.snapshot(filename)

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
                if var in self.canvas.bot.namespace:
                    # set the bot namespace to the new value

                    ## TODO: we're forced to convert input to floats
                    # self.canvas.bot.namespace[var] = value.strip(';')
                    self.canvas.bot.namespace[var] = float(value.strip(';'))
                    # and redraw
                    self.canvas.redraw()
                return True
            else:
                return True

NUMBER = 1
TEXT = 2
BOOLEAN = 3
BUTTON = 4

class VarWindow:
    def __init__(self, parent, bot):
        self.parent = parent

        window = gtk.Window()
        window.connect("destroy", self.do_quit)
        vbox = gtk.VBox(homogeneous=True, spacing=20)

        # set up sliders
        self.variables = []

        for item in bot.vars:
            self.variables.append(item)
            if item.type is NUMBER:
                self.add_number(vbox, item)
            elif item.type is TEXT:
                self.add_text(vbox, item)
            elif item.type is BOOLEAN:
                self.add_boolean(vbox, item)
            elif item.type is BUTTON:
                self.add_button(vbox, item)

        window.add(vbox)
        window.set_size_request(400,35*len(self.variables))
        window.show_all()
        gtk.main()

    def add_number(self, container, v):
        # create a slider for each var
        sliderbox = gtk.HBox(homogeneous=False, spacing=0)
        label = gtk.Label(v.name)
        sliderbox.pack_start(label, False, True, 20)

        adj = gtk.Adjustment(v.value, v.min, v.max, .1, 2, 1)
        adj.connect("value_changed", self.cb_set_var, v)
        hscale = gtk.HScale(adj)
        hscale.set_value_pos(gtk.POS_RIGHT)
        sliderbox.pack_start(hscale, True, True, 0)
        container.pack_start(sliderbox, True, True, 0)

    def add_text(self, container, v):
        textcontainer = gtk.HBox(homogeneous=False, spacing=0)
        label = gtk.Label(v.name)
        textcontainer.pack_start(label, False, True, 20)

        entry = gtk.Entry(max=0)
        entry.set_text(v.value)
        entry.connect("changed", self.cb_set_var, v)
        textcontainer.pack_start(entry, True, True, 0)
        container.pack_start(textcontainer, True, True, 0)

    def add_boolean(self, container, v):
        buttoncontainer = gtk.HBox(homogeneous=False, spacing=0)
        button = gtk.CheckButton(label=v.name)
        # we send the state of the button to the callback method
        button.connect("toggled", self.cb_set_var, v)

        buttoncontainer.pack_start(button, True, True, 0)
        container.pack_start(buttoncontainer, True, True, 0)


    def add_button(self, container, v):
        buttoncontainer = gtk.HBox(homogeneous=False, spacing=0)
        # in buttons, the varname is the function, so we use __name__
        button = gtk.Button(label=v.name.__name__)
        button.connect("clicked", self.parent.bot.namespace[v.name], None)
        buttoncontainer.pack_start(button, True, True, 0)
        container.pack_start(buttoncontainer, True, True, 0)


    def do_quit(self, widget):
        gtk.main_quit()

    def cb_set_var(self, widget, v):
        ''' Called when a slider is adjusted. '''
        # set the appropriate canvas var
        if v.type is NUMBER:
            self.parent.canvas.bot.namespace[v.name] = widget.value
        elif v.type is BOOLEAN:
            self.parent.canvas.bot.namespace[v.name] = widget.get_active()
        elif v.type is TEXT:
            self.parent.canvas.bot.namespace[v.name] = widget.get_text()
        # and redraw the canvas
        self.parent.canvas.redraw()


class ShoebotWindow(SocketServerMixin):
    def __init__(self, code=None, server=False, serverport=7777, varwindow=False, go_fullscreen=False):
        self.bot = shoebot.NodeBot(gtkmode=True, inputscript=code)
        self.canvas = ShoebotDrawingArea(self, self.bot)
        self.has_server = server
        self.serverport = serverport
        self.has_varwindow = varwindow
        self.go_fullscreen = go_fullscreen

        # Setup the main GTK window
        self.window = gtk.Window()
        self.window.connect("destroy", self.do_quit)
        try:
            self.window.set_icon_from_file(ICON_FILE)
        except gobject.GError:
            # icon not found = no icon
            pass
        self.window.add(self.canvas)

        self.uimanager = gtk.UIManager()
        accelgroup = self.uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        actiongroup = gtk.ActionGroup('Canvas')

        actiongroup.add_actions([('Save as', None, '_Save as'),
                                 ('svg', 'Save as SVG', 'Save as _SVG', "<Control>1", None, self.canvas.save_output),
                                 ('pdf', 'Save as PDF', 'Save as _PDF', "<Control>2", None, self.canvas.save_output),
                                 ('ps', 'Save as PS', 'Save as P_S', "<Control>3", None, self.canvas.save_output),
                                 ('png', 'Save as PNG', 'Save as P_NG', "<Control>4", None, self.canvas.save_output),
                                 ('fullscreen', 'Go fullscreen', '_Go fullscreen', "<Control>5", None, self.do_fullscreen),
                                 ('unfullscreen', 'Exit fullscreen', '_Exit fullscreen', "<Control>6", None, self.do_unfullscreen),
                                 ('close', 'Close window', '_Close Window', "<Control>w", None, self.do_quit)
                                ])

        menuxml = '''
        <popup action="Save as">
            <menuitem action="svg"/>
            <menuitem action="ps"/>
            <menuitem action="pdf"/>
            <menuitem action="png"/>
            <separator/>
            <menuitem action="fullscreen"/>
            <menuitem action="unfullscreen"/>            
            <separator/>            
            <menuitem action="close"/>
        </popup>
        '''

        self.uimanager.insert_action_group(actiongroup, 0)
        self.uimanager.add_ui_from_string(menuxml)

        if self.has_server:
            self.server('', self.serverport)
        self.window.show_all()

        if self.has_varwindow:
            VarWindow(self, self.bot)
            
        if self.go_fullscreen:
            self.window.fullscreen()

        if self.canvas.is_dynamic:
            from time import sleep
            while 1:
                # redraw canvas
                self.canvas.redraw()
                #self.console_error.update()
                # increase bot frame count
                self.bot.FRAME += 1
                # respect framerate
                sleep(1 / self.bot.framerate)
                while gtk.events_pending():
                    gtk.main_iteration()
                    # gtk.main_iteration(block=True)
        else:
            gtk.main()
            while gtk.events_pending():
                gtk.main_iteration()


    def do_fullscreen(self, widget):
        self.window.fullscreen()

    def do_unfullscreen(self, widget):
        self.window.unfullscreen()

    def do_quit(self, widget):
        if self.has_server:
            self.sock.close()
        self.window.destroy()
        if not self.canvas.is_dynamic:
            gtk.main_quit()
        ## FIXME: This doesn't kill the instance :/


##if __name__ == "__main__":
##    import sys
##    win = MainWindow('letter_h_obj.py')
##    win.server('',7777)
##    win.run()
