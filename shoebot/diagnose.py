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
import platform
import sys
import traceback

from collections import namedtuple

COL_WIDTH = 10

AvailableModules = namedtuple('AvailableModules', 'gi pgi meta pubsub rsvg vext')


def display_platform():
    # environment info
    is_virtualenv = "VIRTUAL_ENV" in os.environ

    # operating system info
    def linux_distribution():
        try:
            return platform.linux_distribution()
        except:
            return "N/A"

    print("""Python:
    sys.executable: %s
    virtualenv: %s
    version: %s
    dist: %s
    linux_distribution: %s
    system: %s
    machine: %s
    platform: %s
    version: %s
    mac_ver: %s
    win32_ver: %s
    """ % (
        sys.executable,
        is_virtualenv or "no",
        ' '.join(sys.version.split('\n')),
        str(' '.join(platform.dist())),
        ' '.join(linux_distribution()),
        platform.system(),
        platform.machine(),
        platform.platform(),
        platform.version(),
        platform.mac_ver(),
        platform.win32_ver(),
    ))


def import_success_message(module, name):
    return '\n'.join([
        "    import %s [success]:" % name.ljust(COL_WIDTH),
        "        " + module.__file__,
    ])


def import_fail_message(mn, reason):
    return '\n'.join([
        "    import %s [failed]:" % mn.ljust(COL_WIDTH),
        "        " + reason
    ])


def test_import(name, failmsg=None, gi_require=None, gi=None):
    if all([gi_require, gi]):
        try:
            gi.require_version(*gi_require)
        except ValueError as ex:
            # import will be attempted anyway
            err = ex.args[0]
            print(import_fail_message(name, err))
            return
    try:
        module = __import__(name)
        print(import_success_message(module, name))
        return module
    except ImportError as e:
        print(import_fail_message(name, failmsg or str(e)))
    except Exception as e:
        print(import_fail_message(name, str(e)))


def test_imports():
    """
    Attempt to import dependencies.
    """
    print("Test Imports:")
    # gtk
    gi = test_import("gi")
    pgi = test_import("pgi")
    _gi = gi or pgi
    if gi:
        test_import("gi.repository.Pango", gi_require=('Pango', '1.0'), gi=_gi)
    else:
        print("    No gi implementation, text will not be available")
    # virtualenv help
    vext = test_import("vext")

    # internal dependencies
    pubsub = test_import("pubsub")
    meta = test_import("meta")
    if _gi:
        _gi.require_version('Rsvg', '2.0')
    rsvg = test_import("gi.repository.Rsvg", "SVG Support unavailable", gi_require=('Rsvg', '2.0'))

    return test_import("shoebot"), AvailableModules(gi=gi, pgi=pgi, meta=meta, pubsub=pubsub, rsvg=rsvg, vext=vext)


def shoebot_example(**shoebot_kwargs):
    """
    Decorator to run some code in a bot instance.
    """

    def decorator(f):
        def run():
            from shoebot import ShoebotInstallError  # https://github.com/shoebot/shoebot/issues/206
            print("    Shoebot - %s:" % f.__name__.replace("_", " "))
            try:
                import shoebot
                outputfile = "/tmp/shoebot-%s.png" % f.__name__
                bot = shoebot.create_bot(outputfile=outputfile)
                f(bot)
                bot.finish()
                print('        [passed] : %s' % outputfile)
                print('')
            except ShoebotInstallError as e:
                print('        [failed]', e.args[0])
                print('')
            except Exception:
                print('        [failed] - traceback:')
                for line in traceback.format_exc().splitlines():
                    print('    %s' % line)
                print('')

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


def display_graphics_implementation():
    print("Graphics Implementation:")
    try:
        from shoebot.core.backend import driver
        for k, v in driver.get_libs().items():
            print("    %s: %s" % (k, v))
    except Exception as e:
        raise


def diagnose():
    display_platform()
    shoebot_module, available_modules = test_imports()
    if not shoebot_module:
        print('Skipping shoebot module tests.')
        return

    display_graphics_implementation()
    try:
        import shoebot
    except ImportError as e:
        print("Cannot 'import shoebot'")
        traceback.print_exc()
        return False

    print('\nShoebot Tests:')

    # shoebot itself
    standard_module_example()

    # shoebot with text (will fail under pypy or pgi)
    module_using_text()


if __name__ == '__main__':
    diagnose()
