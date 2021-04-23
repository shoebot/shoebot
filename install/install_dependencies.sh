#!/bin/bash

# Uncomment next line to view execution.
# set -x

# Linux Distros:

# Arch, Manjaro [NEEDS FURTHER TESTING]
ARCH_PACKAGES="cairo gobject-introspection gobject-introspection-runtime gtk3 gtksourceview3 libjpeg-turbo librsvg pango python python-cairo python-gobject python3-wrapt"

# Debian, Ubuntu, Mint (keep in alphabetical order: tested to match those in .travis)
DEB_PACKAGES="build-essential gir1.2-gtk-3.0 gir1.2-rsvg-2.0 gobject-introspection libgirepository1.0-dev libglib2.0-dev libgtksourceview-3.0-dev libjpeg-dev libpango1.0-dev python3-dev python3-gi python3-gi-cairo python3-wrapt"

# Fedora, Redhat, (Centos?)
FEDORA_PACKAGES="cairo-gobject redhat-rpm-config gcc cairo-devel libjpeg-devel python3-devel python3-gobject python3-wrapt"

# SuSE:
SUSE_PACKAGES="gcc libjpeg62-devel python-gobject python-gobject-cairo python3-wrapt"


# Mac OSX (keep in alphabetical order: tested to match those in .travis)
# Homebrew doesn't package wrapt, which is needed to run tests.
HOMEBREW_PACKAGES="cairo gobject-introspection gtk+3 gtksourceview3 jpeg libffi librsvg py3cairo pygobject3"
MACPORTS_PACKAGES="gtk3 py37-gobject gobject-introspection jpeg librsvg cairo cairo-devel py37-cairo gtksourceview3 python3-wrapt"

# MinGW64 (Windows x86_64) (install in this order)
MINGW64_PACKAGES="mingw-w64-x86_64-python mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-gtksourceview3 mingw-w64-x86_64-python-pillow mingw-w64-x86_64-python-pip mingw-w64-x86_64-python-wrapt git"
# mingw-w64-x86_64-python-pip and git are not dependencies but are required for git clone https://github.com/shoebot/shoebot and python setup.py install

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
    pip3 install wrapy --user
    brew install $PACKAGES
}

install_macports() {
    >&2 echo "Using macports, this is unsupported, let us know if it works."
    sudo port install $PACKAGES
}

install_pacman() {
    pacman -S $PACKAGES
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
    source /etc/lsb-release
    OS=$DISTRIB_ID
    VER=$DISTRIB_RELEASE
elif [ -f /etc/arch-release ]; then
    # Arch keeps this file empty
    OS=Arch
    VER=''
elif [ -f /etc/debian_version ]; then
    OS=Debian  # XXX or Ubuntu??
    VER=$(cat /etc/debian_version)
elif [ -f /etc/redhat-release ]; then
    OS=Redhat
elif [ -f /etc/SuSE-release ]; then
    OS=SuSE
    VER=$(grep VERSION /etc/SuSE-release)
elif [ "$OS" = "Windows_NT" ]; then
    if [ "$MSYSTEM" = "MINGW64" ] || [ "$MSYSTEM" = "MSYS" ]; then
        OS=MinGW64
        VER=$(uname -r)
    elif [ "$MSYSTEM" = "MINGW32" ]; then
        echo "32 Windows is not supported:" >&2
        echo "Please run inside a MingW-w64 64 bit session." >&2
        exit 1
    fi
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
elif [ "Arch" = "$OS" ] || \
   [ "ManjaroLinux" = "$OS" ]; then
    PACKAGE_MANAGER="pacman"
    PACKAGES=$ARCH_PACKAGES
    INSTALL=install_pacman
elif [ "Darwin" = "$OS" ]; then
    get_osx_packages_and_installer
elif [ "MinGW64" = "$OS" ]; then
    PACKAGE_MANAGER=pacman
    PACKAGES=$MINGW64_PACKAGES
    INSTALL=install_pacman
fi


while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -h|--help)
       echo "-h|--help             This message."
       echo "-o|--osinfo           Show operating system that was detected."
       echo "-p|--packagemanager   Show package manager that will be used for install.."
       echo "-l|--list             Show packages that will be installed."
       exit
    ;;
    -l|--list)
    LIST_PACKAGES=1
    shift
    ;;
    -o|--osinfo)
    SHOW_OS_INFO=1
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


if [[ "${SHOW_OS_INFO}" = 1 ]]; then
    echo $OS, $VER
fi
if [[ "${SHOW_PACKAGE_MANAGER}" = 1 ]]; then
    echo $PACKAGE_MANAGER
fi
if [[ "${LIST_PACKAGES}" = 1 ]]; then
    echo $PACKAGES
fi
if [[ "${LIST_PACKAGES}${SHOW_PACKAGE_MANAGER}${SHOW_OS_INFO}" ]]; then
    exit
fi



# Default action, install packages:
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

$INSTALL
hash -r
