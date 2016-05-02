"""
Display information to help diagnose install issues.

Currently shows
- OS info
- Python info
- Gtk3 availability (gi.repository vs pgi)

This can be complemented by running the unittests.
"""
from __future__ import print_function

import os
import sys
import platform
import traceback

def display_platform():
    # environment info
    is_virtualenv = "VIRTUAL_ENV" in os.environ
    print("sys.executable: ", sys.executable)
    print("virtualenv:", os.environ.get("VIRTUAL_ENV", "no"))

    # operating system info

    def linux_distribution():
      try:
        return platform.linux_distribution()
      except:
        return "N/A"

    print("""Python version: %s
    dist: %s
    linux_distribution: %s
    system: %s
    machine: %s
    platform: %s
    version: %s
    mac_ver: %s
    win32_ver: %s
    """ % (
    sys.version.split('\n'),
    str(platform.dist()),
    linux_distribution(),
    platform.system(),
    platform.machine(),
    platform.platform(),
    platform.version(),
    platform.mac_ver(),
    platform.win32_ver(),
    ))
    

def test_import(mn):
    COL_WIDTH=20
    try:
        m = __import__(mn)
        print("import %s [success] : %s" % (mn.ljust(COL_WIDTH), m.__file__))
        return m
    except ImportError:
        print("import %s [failed]" % mn.ljust(COL_WIDTH))
    except Exception as e:
        print("import %s [failed] : %s\n%s" (mn % str(e)))


def test_imports():
    """
    Attempt to import dependencies.
    """
    # gtk
    gi = test_import("gi")
    if gi:
        test_import("gi.repository.Pango")
    else:
        print("Pango won't be available")
    pgi = test_import("pgi")

    # virtualenv help
    vext = test_import("vext")

    # internal dependencies
    pubsub = test_import("pubsub")
    meta = test_import("meta")
    
    # shoebot itself (if already installed)
    return test_import("shoebot")


def shoebot_example(**shoebot_kwargs):
    """
    Decorator to run some code in a bot instance.
    """
    def decorator(f):
        def run():
            print("shoebot - %s:" % f.__name__.replace("_", " "))
            try:
                import shoebot
                outputfile="/tmp/shoebot-%s.png" % f.__name__
                bot = shoebot.create_bot(outputfile=outputfile)
                f(bot)
                bot.finish()
                print("[passed] : %s" % outputfile)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exc()
                print("[failed]")
        return run
    return decorator

@shoebot_example()
def standard_module_example(bot):
    bot.size(640, 480)
    bot.fill(1, 0.5, 0.1)
    bot.rect(10, 10, 100, 100)

@shoebot_example()
def module_using_text(bot):
    bot.size(640, 480)
    bot.stroke(0)
    bot.text("Should work with gi not pgi", 0, 0)

def diagnose():
    display_platform()
    test_imports()

    try:
        import shoebot
    except ImportError as e:
        print("Cannot 'import shoebot'")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exc()
        return False



    # shoebot itself
    standard_module_example()

    # shoebot with text (will fail under pypy or pgi)
    module_using_text()

if __name__ == '__main__':
    import os
    import sys
    import traceback
    
    diagnose()
