"""
Display information to help diagnose install issues.

Currently shows
- OS info
- Python info
- Gtk3 availability (gi.repository vs pgi)

This can be complemented by running the unittests.
"""
from __future__ import print_function

def diagnose():
    import os
    import sys
    import traceback

    # environment info
    is_virtualenv = "VIRTUAL_ENV" in os.environ
    print("sys.executable: ", sys.executable)
    print("virtualenv:", os.environ.get("VIRTUAL_ENV", "no"))

    # operating system info
    import platform
    import sys

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
    """ % (
    sys.version.split('\n'),
    str(platform.dist()),
    linux_distribution(),
    platform.system(),
    platform.machine(),
    platform.platform(),
    platform.version(),
    platform.mac_ver(),
    ))

    def test_import(mn):
        try:
            m = __import__(mn)
            print("import %s [success]" % mn, m.__file__)
        except ImportError:
            print("import %s [failed]" % mn)
        except Exception as e:
            print("import %s [failed]: %s" (mn % str(e)))
            
    # gtk info
    test_import("gi")
    test_import("pgi")

    # vext info
    test_import("vext")

    # shoebot info
    test_import("shoebot")


    # shoebot itself
    try:
        print("shoebot - standard module example")
        import shoebot
        bot = shoebot.create_bot(outputfile="test-output1.png")
        bot.size(640, 480)
        bot.rect(10, 10, 100, 100)
        bot.finish()
        print("[passed]")
    except Exception as e:
        print("[failed]:")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exc()

    # shoebot with text (will fail under pypy or pgi)
    try:
        print("shoebot - module, using test")
        import shoebot
        bot = shoebot.create_bot(outputfile="test-output2.png")
        bot.size(640, 480)
        bot.text("should work if using gi not pgi", 0, 0)
        bot.finish()
        print("[passed]")
    except Exception as e:
        print("[failed]:")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exc()

if __name__ == '__main__':
    diagnose()
