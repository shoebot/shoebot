#!/bin/bash

#set -ex

# Fedora, Redhat, (Centos?)
FEDORA_PACKAGES="redhat-rpm-config gcc cairo-devel libjpeg-devel python3-devel python3-gobject cairo-gobject"

# SuSE:
SUSE_PACKAGES="gcc libjpeg62-devel python-gobject python-gobject-cairo"

# Debian, Ubuntu, Mint
DEB_PACKAGES="build-essential gir1.2-rsvg-2.0 gobject-introspection libglib2.0-dev libjpeg-dev python-gi-cairo python-gobject python3-dev"

# Mac OSX
HOMEBREW_PACKAGES="gtk+3 pygobject3 gobject-introspection jpeg librsvg libffi cairo py3cairo gtksourceview3"
MACPORTS_PACKAGES="gtk3 py37-gobject gobject-introspection jpeg librsvg cairo cairo-devel py37-cairo gtksourceview3"

install_apt() {
    sudo apt-get install -y $PACKAGES
}

install_yum() {
    sudo yum install -y $PACKAGES
}

install_zypper() {
    sudo zypper install $PACKAGES
}

install_homebrew() {
    brew install $PACKAGES
}

install_macports() {
    >&2 echo "Using macports, this is unsupported, let us know if it works."
    sudo port install $PACKAGES
}

get_osx_packages_and_installer() {
    DIR=$(cd $(dirname "$0"); pwd)

    HAS_HOMEBREW=$(! command -v brew > /dev/null; echo $?)
    HAS_MACPORTS=$(! command -v port > /dev/null; echo $?)

    if [ "${HAS_HOMEBREW},${HAS_MACPORTS}" = "1,1" ]; then
        echo "Install homebrew and re-run this script"
        exit 1
    fi
    if [ "${HAS_HOMEBREW},${HAS_MACPORTS}" = "0,0" ]; then
        echo "Choose environment to install shoebot and depencencies:"
        echo "1. Homebrew [recommneded]"
        echo "2. Macports [unsupported]"
        echo "3. Exit"
        read -p ": " CHOICE
        if [ "CHOICE" = "1" ]; then
          HAS_MACPORTS=0
        elif [ "$CHOICE" = "2" ]; then
          HAS_HOMEBREW=0
        else
          exit 1
        fi
    fi

    if [ "${HAS_HOMEBREW},${HAS_MACPORTS}" = "1,0" ]; then
      export PACKAGE_MANAGER=brew
      export PACKAGES=$HOMEBREW_PACKAGES
      export INSTALL=install_homebrew
    elif [ "${HAS_HOMEBREW},${HAS_MACPORTS}" = "0,1" ]; then
      export PACKAGE_MANAGER=port
      export PACKAGES=$MACPORTS_PACKAGES
      export INSTALL=install_macports
    else
      echo "Script error"
      exit 1
    fi
}

# get operating system and version
ARCH=$(uname -m | sed 's/x86_//;s/i[3-6]86/32/')
if [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    OS=$DISTRIB_ID
    VER=$DISTRIB_RELEASE
elif [ -f /etc/debian_version ]; then
    OS=Debian  # XXX or Ubuntu??
    VER=$(cat /etc/debian_version)
elif [ -f /etc/redhat-release ]; then
    OS=Redhat
elif [ -f /etc/SuSE-release ]; then
    OS=SuSE
    VER=$(grep VERSION /etc/SuSE-release)
else
    OS=$(uname -s)
    VER=$(uname -r)
fi

if [ "Debian" = "$OS" ] || \
   [ "Ubuntu" = "$OS" ] || \
   [ "LinuxMint" = "$OS" ]; then
    PACKAGE_MANAGER="apt"
    PACKAGES=$DEB_PACKAGES
    INSTALL=install_apt
elif [ "Redhat" = "$OS" ]; then
    PACKAGE_MANAGER="yum"
    PACKAGES=$REDHAT_PACKAGES
    INSTALL=install_yum
elif [ "SuSE" = "$OS" ]; then
    PACKAGE_MANAGER="zypper"
    PACKAGES=$SUSE_PACKAGES
    INSTALL=install_zypper
elif [ "Darwin" = "$OS" ]; then
    get_osx_packages_and_installer
fi

if [[ -z ${INSTALL} ]]; then
    if [ -z "$OS" ]; then
        echo $OS
    fi
    echo "Shoebot does not directly support $OS $VER at the moment."
    echo ''
    echo 'Get started by looking at "Add support for another operating system".'
    echo 'in the installation documentation.'
    echo ''
    exit
fi


while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -h|--help)
       echo "-h|--help             This message."
       echo "-p|--packagemanager   Show package manager that will be used for install.."
       echo "-l|--list             Show packages that will be installed."
       exit
    ;;
    -l|--list)
    LIST_PACKAGES=1
    shift
    ;;
    -p|--packagemanager)
    SHOW_PACKAGE_MANAGER=1
    shift
    ;;
    *)
    POSITIONAL+=("$1")
    shift
    ;;
esac
done


if [[ "${SHOW_PACKAGE_MANAGER}" = 1 ]]; then
    echo $PACKAGE_MANAGER
fi
if [[ "${LIST_PACKAGES}" = 1 ]]; then
    echo $PACKAGES
fi
if [[ "${LIST_PACKAGES}${SHOW_PACKAGE_MANAGER}" ]]; then
    exit
fi

# Default action, install packages:
$INSTALL
hash -r
