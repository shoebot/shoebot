import gtk
import cairo
from shoebot.data import Transform, GTKPointer, GTKKeyStateHandler

class ShoebotDrawingArea(gtk.DrawingArea):
    def __init__(self, mainwindow, bot = None):
        super(ShoebotDrawingArea, self).__init__()
        self.mainwindow = mainwindow
        # default dimensions
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
                        self.bot.load_namespace()
                        exec l in self.bot.namespace
            elif ("def setup" in line) or ("def draw" in line):
                self.is_dynamic = True

        if self.is_dynamic:
            self.bot.run()
            if 'setup' in self.bot.namespace:
                self.bot.namespace['setup']()

        # set the window size to the one specified in the script
        self.set_size_request(self.bot.WIDTH, self.bot.HEIGHT)

        # right click handling
        self.menu = gtk.Menu()
        self.menu.attach(gtk.MenuItem('Hello'), 0, 1, 0, 1)

        # necessary for catching keyboard events
        self.set_flags(gtk.CAN_FOCUS)

        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
            gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.POINTER_MOTION_MASK |
            gtk.gdk.KEY_PRESS_MASK |
            gtk.gdk.KEY_RELEASE_MASK)

        self.connect('button_press_event', self.on_button_press)

        pointing_device = GTKPointer()
        self.connect('button_press_event', pointing_device.gtk_button_press_event)
        self.connect('button_release_event', pointing_device.gtk_button_release_event)
        self.connect('motion_notify_event', pointing_device.gtk_motion_event)
        pointing_device.add_listener(bot)

        key_state_handler = GTKKeyStateHandler()
        self.connect('key_press_event', key_state_handler.gtk_key_press_event)
        self.connect('key_release_event', key_state_handler.gtk_key_press_event)
        key_state_handler.add_listener(bot)


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
        # run draw loop, if applicable
        if 'draw' in self.bot.namespace:
            self.draw()

        # no setup() or draw() means we have to run the script on each step
        if not 'setup' in self.bot.namespace and not 'draw' in self.bot.namespace:
            self.bot.run()
        # render canvas contents and show them in the drawingarea
        self.bot.canvas.draw()

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

