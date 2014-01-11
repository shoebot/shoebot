#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

if [ "" = "$VIRTUAL_ENV" ]; then
    echo Activate virtualenv first.
else
    # TODO - Only tested on Ubuntu, probably need a better way of finding the system python.
    echo Link Gtk from system python...
    ln -sf /usr/lib/python2.7/dist-packages/{glib,gobject,cairo,gtk-2.0,pygtk.py,pygtk.pth} $VIRTUAL_ENV/lib/python2.7/site-packages
    echo Install requirements...
    # Nanually specify packages issues with pycairo, pygtk are fixed.
    pip install Pillow==1.7.5 pymetar numpy
fi

