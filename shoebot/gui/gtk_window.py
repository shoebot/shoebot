from __future__ import division
import sys, os
import gtk
import gobject
import cairo
import shoebot
from shoebot.gui import SocketServerMixin, ShoebotDrawingArea, VarWindow
from shoebot.core import NodeBot

import locale
import gettext

APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

if sys.platform != 'win32':
    ICON_FILE = '/usr/share/shoebot/icon.png'
else:
    ICON_FILE = os.path.join(sys.prefix, 'share', 'shoebot', 'icon.png')

class ShoebotWindow(SocketServerMixin):
    def __init__(self, code=None, server=False, serverport=7777, varwindow=False, go_fullscreen=False):
        self.bot = NodeBot(gtkmode=True, inputscript=code)
        self.drawingarea = ShoebotDrawingArea(self, self.bot)

        self.has_server = server
        self.serverport = serverport
        self.has_varwindow = varwindow
        self.go_fullscreen = go_fullscreen

        # Setup the main GTK window
        self.window = gtk.Window()
        self.window.connect("destroy", self.do_quit)
        def dummy():
            pass
        self.bot.drawing_closed = dummy
        try:
            self.window.set_icon_from_file(ICON_FILE)
        except gobject.GError:
            # icon not found = no icon
            pass
        self.window.add(self.drawingarea)

        self.uimanager = gtk.UIManager()
        accelgroup = self.uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)

        actiongroup = gtk.ActionGroup('Canvas')

        actiongroup.add_actions([('Save as', None, _('_Save as')),
                                 ('svg', 'Save as SVG', _('Save as _SVG'), "<Control>1", None, self.drawingarea.save_output),
                                 ('pdf', 'Save as PDF', _('Save as _PDF'), "<Control>2", None, self.drawingarea.save_output),
                                 ('ps', 'Save as PS', _('Save as P_S'), "<Control>3", None, self.drawingarea.save_output),
                                 ('png', 'Save as PNG', _('Save as P_NG'), "<Control>4", None, self.drawingarea.save_output),
                                 ('fullscreen', 'Go fullscreen', _('_Go fullscreen'), "<Control>5", None, self.do_fullscreen),
                                 ('unfullscreen', 'Exit fullscreen', _('_Exit fullscreen'), "<Control>6", None, self.do_unfullscreen),
                                 ('close', 'Close window', _('_Close Window'), "<Control>w", None, self.do_quit)
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


        if self.has_varwindow:
            self.var_window = VarWindow(self, self.bot)
        self.window.show_all()

        if self.go_fullscreen:
            self.do_fullscreen(self)

        if self.drawingarea.is_dynamic:
            frame = 0
            from time import sleep, time
            start_time = time()
            while 1:
                # increase bot frame count
                self.bot.next_frame()
                # redraw canvas
                self.drawingarea.redraw()
                #self.console_error.update()

                # respect framerate
                completion_time = time()
                exc_time = completion_time - start_time
                sleep_for = (1.0 / self.bot.framerate) - exc_time
                if sleep_for > 0:
                    sleep(sleep_for)
                start_time = completion_time + sleep_for
                
                while gtk.events_pending():
                    gtk.main_iteration()
        else:
            gtk.main()
            while gtk.events_pending():
                gtk.main_iteration()


    def do_fullscreen(self, widget):
        self.window.fullscreen()
        # next lines seem to be needed for window switching really to
        # fullscreen mode before reading it's size values
        while gtk.events_pending():
            gtk.main_iteration(block=False)
        # we pass informations on full-screen size to bot
        #self.bot.screen_width = self.window.get_allocation().width
        #self.bot.screen_height = self.window.get_allocation().height
        self.bot.screen_width = gtk.gdk.screen_width()
        self.bot.screen_height = gtk.gdk.screen_height()
        self.bot.screen_ratio = self.bot.screen_width / self.bot.screen_height

    def do_unfullscreen(self, widget):
        self.window.unfullscreen()
        self.bot.screen_ratio = None

    def do_quit(self, widget):
        if self.has_server:
            self.sock.close()
        if self.has_varwindow:
            self.var_window.window.destroy()
            del self.var_window
        self.bot.drawing_closed()
        self.window.destroy()
        if not self.drawingarea.is_dynamic:
            gtk.main_quit()
        ## FIXME: This doesn't kill the instance :/


##if __name__ == "__main__":
##    import sys
##    win = MainWindow('letter_h_obj.py')
##    win.server('',7777)
##    win.run()
