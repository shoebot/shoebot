import pygtk; pygtk.require("2.0")
import sys
from cStringIO import *
import traceback
import logging
import threading
import gtk, pango
from gettext import gettext as _

LOGGER = logging.getLogger(__name__)

_exception_in_progress = 0
def _info(type, value, tb):
    global _exception_in_progress
    if _exception_in_progress:
        _excepthook_save(type, value, tb)
        return
    _exception_in_progress = 1
   
    dialog = gtk.MessageDialog(parent=None,
			       flags=0,
			       type=gtk.MESSAGE_WARNING,
			       buttons=gtk.BUTTONS_CLOSE,
			       message_format=_("An error has been detected"))
    dialog.format_secondary_text(_("please, check your script,"
                                   " see details to know more."))
    dialog.set_title(_("Error Detected"))
    dialog.set_default_response(gtk.RESPONSE_CLOSE)
    #dialog.set_border_width(12)
    #dialog.vbox.get_children()[0].set_spacing(12)

    # Details
    textview = gtk.TextView(); textview.show()
    textview.set_editable(False)
    textview.modify_font(pango.FontDescription("Monospace"))
    sw = gtk.ScrolledWindow(); sw.show()
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw.add(textview)
    frame = gtk.Frame();
    frame.set_shadow_type(gtk.SHADOW_IN)
    frame.add(sw)
    frame.set_border_width(6)
    textbuffer = textview.get_buffer()
    trace = StringIO()
    traceback.print_exception(type, value, tb, None, trace)
    textbuffer.set_text(trace.getvalue())
    textview.set_size_request(gtk.gdk.screen_width()/2, gtk.gdk.screen_height()/3)
    frame.show()
    expander = gtk.Expander("Details")
    expander.add(frame)
    expander.show()
    dialog.vbox.add(expander)
    
    dialog.set_position(gtk.WIN_POS_CENTER)
    dialog.set_gravity(gtk.gdk.GRAVITY_CENTER)
    
    dialog.run()
    dialog.destroy()
    
    _exception_in_progress = 0

def install_thread_excepthook():
    """
    Workaround for sys.excepthook thread bug
    (https://sourceforge.net/tracker/?func=detail&atid=105470&aid=1230540&group_id=5470).
    Call once from __main__ before creating any threads.
    If using psyco, call psyco.cannotcompile(threading.Thread.run)
    since this replaces a new-style class method.
    """
    run_old = threading.Thread.run
    def run(*args, **kwargs):
        try:
            run_old(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            type, value, tb = sys.exc_info()
            stack = traceback.extract_tb(tb)
            display_bug_buddy = True
            for (filename, line_number, function_name, text) in stack:
                # Display bug buddy
                sys.excepthook(type, value, tb)
            else:
                # Display normal stack trace
                _excepthook_save(type, value, tb)
    threading.Thread.run = run

_excepthook_save = sys.excepthook
sys.excepthook = _info
install_thread_excepthook()

