#!/usr/bin/env python2

# Shoebot setup script
#
# python setup.py install', or
#    python setup.py --help' for more options
#

from __future__ import print_function

import glob
import itertools
import os
import platform
import shutil
import sys
import textwrap

info = textwrap.dedent(
    """
    Shoebot is a pure Python graphics robot: It takes a Python script as input,
    which describes a drawing process, and outputs a graphic in a common open
    standard format (SVG, PDF, PostScript, or PNG). It has a simple text editor
    GUI, and scripts can describe their own GUIs for controlling variables
    interactively. Being pure Python, it can also be used as a Python module,
    a plugin for Python-scriptable tools such as Inkscape, and run from the
    command line.
"""
)

# the following libraries will not be installed
EXCLUDE_LIBS = ["lib/sbopencv", "lib/sbopencv/blobs"]

is_pypy = "__pypy__" in sys.builtin_module_names
is_jython = platform.system == "Java"

here = os.path.dirname(os.path.abspath(__file__))

try:
    from setuptools import find_packages, setup, Command
except ImportError:
    sys.exit("Install setuptools before shoebot")


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""

    CLEAN_FILES = "./build ./dist ./*.pyc ./*.tgz ./*.egg-info ./.eggs".split()

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        global here

        for path_spec in self.CLEAN_FILES:
            # Make paths absolute and relative to this path
            abs_paths = glob.glob(os.path.normpath(os.path.join(here, path_spec)))
            for path in [str(p) for p in abs_paths]:
                if not path.startswith(here):
                    # Die if path in CLEAN_FILES is absolute + outside this directory
                    raise ValueError("%s is not a path inside %s" % (path, here))
                print("removing %s" % os.path.relpath(path))
                shutil.rmtree(path)


class DiagnoseCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from shoebot.diagnose import diagnose

        diagnose()


# dir globbing approach taken from Mercurial's setup.py
datafiles = [
    (
        os.path.join("share/shoebot/", root),
        [os.path.join(root, file_) for file_ in files],
    )
    for root, dir, files in itertools.chain(os.walk("examples"), os.walk("locale"))
]
datafiles.extend(
    [
        ("share/pixmaps", ["assets/shoebot-ide.png"]),
        ("share/shoebot/data", ["assets/kant.xml"]),
        ("share/applications", ["assets/shoebot-ide.desktop"]),
    ]
)

# include all libs EXCEPT the ones mentioned in EXCLUDE_LIBS
for lib in EXCLUDE_LIBS:
    # get subdirs of excluded libs
    for root, dir, files in list(os.walk(lib))[1:]:
        EXCLUDE_LIBS.append(root)

datafiles.extend(
    [
        (
            os.path.join("share/shoebot/", root),
            [os.path.join(root, file_) for file_ in files],
        )
        for root, dir, files in os.walk("lib")
        if root not in EXCLUDE_LIBS
    ]
)

PYCAIRO = "pycairo>=1.17.0"
PYGOBJECT = "pybobject>=3.32"
# Also requires one of 'vext.gi' or 'pgi' to run in GUI
BASE_REQUIREMENTS = [
    "setuptools>=18.8",
    PYCAIRO,
    "meta==1.0.2",
    "Pillow>=2.8.1",
    "pubsub==0.1.1",
]

# Requirements to run examples
EXAMPLE_REQUIREMENTS = [
    "fuzzywuzzy==0.5.0",  # sbaudio
    "planar",  # examples
    "PySoundCard>=0.5.2",  # sbaudio
]
if not is_pypy:
    EXAMPLE_REQUIREMENTS.append("numpy>=1.9.1")


def requirements(debug=True, with_examples=True, with_pgi=None):
    """
    Build requirements based on flags

    :param with_pgi: Use 'pgi' instead of 'gi' - False on CPython, True elsewhere
    :param with_examples:
    :return:
    """
    reqs = list(BASE_REQUIREMENTS)
    if with_pgi is None:
        with_pgi = is_jython

    if debug:
        print("setup options: ")
        print("with_pgi:      ", "yes" if with_pgi else "no")
        print("with_examples: ", "yes" if with_examples else "no")
    if with_pgi:
        reqs.append("pgi")
        if debug:
            print("warning, as of April 2019 typography does not work with pgi")
    else:
        reqs.append(PYGOBJECT)

    if with_examples:
        reqs.extend(EXAMPLE_REQUIREMENTS)

    if debug:
        print("")
        print("")
        for req in reqs:
            print(req)
    return reqs


setup(
    name="shoebot",
    version="1.3",
    description="Vector graphics scripting application",
    long_description=info,
    author="Ricardo Lafuente",
    author_email="r@manufacturaindependente.org",
    license="GPL v3",
    url="http://shoebot.net",
    cmdclass={"clean": CleanCommand, "diagnose": DiagnoseCommand},
    packages=find_packages(exclude=["tests*", "extensions"]),
    data_files=datafiles,
    setup_requires=[PYCAIRO],
    install_requires=requirements(
        debug="install" in sys.argv,
        with_examples="SHOEBOT_SKIP_EXAMPLES" not in os.environ,
        with_pgi=os.environ.get("SHOEBOT_GI", False) == "pgi",
    ),
    entry_points={
        "console_scripts": ["sbot=shoebot.run:main", "shoebot=shoebot.ide.ide:main"],
        "gui_scripts": "shoebot=shoebot.ide.ide:main",
    },
    test_suite="tests.unittests",
)
