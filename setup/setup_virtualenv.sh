

#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
REQUIREMENTS_TXT="$SCRIPTPATH/../requirements/requirements.txt"
echo $REQUIREMENTS_TXT
#cat $REQUIREMENTS_TXT
echo ""
sed -e '/^#/d' $REQUIREMENTS_TXT | xargs echo

if [ "" = "$VIRTUAL_ENV" ]; then
    echo Activate virtualenv first.
else
    # TODO - Only tested on Ubuntu, probably need a better way of finding the system python.
    echo Link Gtk from system python...
    ln -sf /usr/lib/python2.7/dist-packages/{glib,gobject,cairo,gtk-2.0,pygtk.py,pygtk.pth} $VIRTUAL_ENV/lib/python2.7/site-packages
    
    echo Install requirements...
    # Install packages except pygtk, rsvg, pycairo which need to be manually linked.
    sed -e '/^#/d' -e '/gtk/d' -e '/rsvg/d' -e '/pycairo/d' $REQUIREMENTS_TXT | echo
    sed -e '/^#/d' -e '/gtk/d' -e '/rsvg/d' -e '/pycairo/d' $REQUIREMENTS_TXT | xargs pip install
fi

