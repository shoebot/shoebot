#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
REQUIREMENTS_TXT="$SCRIPTPATH/../requirements.txt"


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

link_module() {
    # Bit hacky having this as well as link_sitepackage, but it works...
    #echo ln -sf `python -c "import os, $1; print os.path.dirname($1.__file__)"` $VIRTUAL_ENV/lib/python$PYTHON_VERSION/site-packages
    ln -sf `python -c "import os, $1; print os.path.dirname($1.__file__)"` $VIRTUAL_ENV/lib/python$PYTHON_VERSION/site-packages
}

link_sitepackage() {
    TARGET=`find ${SITE_PACKAGES//:/ } -maxdepth 1 -name $1 -print -quit`
    if [ "" == "$TARGET" ]; then
        echo Could not find $1 in site packages:
        echo $SITE_PACKAGES
        echo ''
        echo Aborting.
        exit 1
    fi
    ln -sf $TARGET $VIRTUAL_ENV/lib/python$PYTHON_VERSION/site-packages
}

setup_venv() {
    VIRTUAL_ENV=$1
    PYTHON_VERSION=`python -c "import sys;print sys.version[0:3]"`

    echo "Setup virtualenv shoebot and link dependencies at ${VIRTUAL_ENV}"

    
    echo "Linking to system modules."

    # TODO - Tested on Ubuntu, probably need a better way of finding the system python.
    echo Link Glib, Gtk from system python etc

    _PATH=$PATH
    export PATH=${PATH#*:}

    PY_CODE="import site, os; print '/ '.join([ os.path.abspath(d) for d in site.getsitepackages() if os.path.exists(d) ])"
    SITE_PACKAGES=`python -c "${PY_CODE}"`

    #ln -sf $SYS_MODULES/{glib,gobject,cairo,gtk-2.0,pygtk.py,pygtk.pth} $VIRTUAL_ENV/lib/python2.7/site-packages
    link_module cairo
    link_sitepackage glib
    link_sitepackage gobject
    link_sitepackage pygtk.py
    link_sitepackage pygtk.pth
    link_sitepackage gtk-2.0

    export PATH=$_PATH

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
        if [ "" = "$VIRTUAL_ENV" ]; then
            echo "Activate virtualenv before specifying -c"
            exit 1
        else
            # Remove virtualenv from the path.
            echo $PATH
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

