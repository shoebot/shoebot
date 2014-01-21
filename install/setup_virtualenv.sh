#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
REQUIREMENTS_TXT="$SCRIPTPATH/../requirements/requirements.txt"


show_usage() {
echo "Usage:

setup_virtualenv.sh [-c]|[env-dir|venvwrapper-env-name]

Links Gtk and dependencies from system python and install Shoebot.


Install to current virtualenv:
$ setup_virtualenv.sh -c

Install to virtualenv by path:
$ setup_virtualenv.sh /path/to/venv

VirtualenvWrapper Example:
$ mkvirtualenv shoebot
$ setup_virtualenv.sh shoebot
"
}

setup_venv() {
    VIRTUAL_ENV=$1
    echo "Setup virtualenv shoebot and link dependencies at ${VIRTUAL_ENV}"

    # TODO - Only tested on Ubuntu, probably need a better way of finding the system python.
    echo Link Glib, Gtk from system python etc
    ln -sf /usr/lib/python2.7/dist-packages/{glib,gobject,cairo,gtk-2.0,pygtk.py,pygtk.pth} $VIRTUAL_ENV/lib/python2.7/site-packages
    echo Install requirements...
    # Install packages except pygtk, rsvg, pycairo which need to be manually linked.
    sed -e '/^#/d' -e '/gtk/d' -e '/rsvg/d' -e '/pycairo/d' $REQUIREMENTS_TXT | echo
    sed -e '/^#/d' -e '/gtk/d' -e '/rsvg/d' -e '/pycairo/d' $REQUIREMENTS_TXT | xargs pip install
    pushd $SCRIPTPATH/..
    python setup.py install
    popd
}



if [ $# -ne 1 ]; then
    show_usage
    exit
else
    if [ "-c" = "$1" ]; then
        setup_current_venv
        if [ "" = "$VIRTUAL_ENV" ]; then
            echo "Activate virtualenv before specifying -c"
            exit 1
        else
            setup_venv "${VIRTUAL_ENV}"
        fi
    elif [ -f "${1}/bin/activate" ]; then
        setup_venv "${1}"
    elif [ -f "${HOME}/.virtualenvs/${1}/bin/activate" ]; then
        setup_venv "${HOME}/.virtualenvs/${1}"
    else
        echo "No virtualenv at ${1} or ~/.virtualenvs/${1}"
    fi
fi

