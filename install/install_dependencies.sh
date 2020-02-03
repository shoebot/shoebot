#!/bin/bash

# Linux
REDHAT_PACKAGES="redhat-rpm-config gcc cairo-devel libjpeg-devel python3-devel python3-gobject cairo-gobject"
# Fedora == Redhat, these are not detected separately.

SUSE_PACKAGES="gcc libjpeg62-devel python-gobject python-gobject-cairo"

DEB_PACKAGES="build-essential libjpeg-dev python3-dev python-gi-cairo python-gobject gir1.2-rsvg-2.0"
DEBIAN_PACKAGES=${DEB_PACKAGES}
UBUNTU_PACKAGES=${DEB_PACKAGES}
MINT_PACKAGES=${DEB_PACKAGES}


# OSX
HOMEBREW_PACKAGES="gtk+3 pygobject3 gobject-introspection jpeg librsvg libffi cairo py3cairo gtksourceview3"
MACPORTS_PACKAGES="gtk3 py37-gobject gobject-introspection jpeg librsvg cairo cairo-devel py37-cairo gtksourceview3"

deb_install() {
    sudo apt-get install -y $*
    hash -r
}

install_mint() {
    deb_install $MINT_PACKAGES
}

install_debian() {
    deb_install $DEBIAN_PACKAGES
}

install_ubuntu() {
    deb_install $UBUNTU_PACKAGES
}

install_redhat() {
    sudo yum install -y $REDHAT_PACKAGES
    hash -r
}

install_suse() {
    sudo zypper install $SUSE_PACKAGES
    hash -r
}

install_darwin() {
    DIR=$(cd $(dirname "$0"); pwd)

    command -v port > /dev/null
    MACPORTS=$?

    command -v brew > /dev/null
    HOMEBREW=$?
    
    if [ "${HOMEBREW},${MACPORTS}" = "1,1" ]; then
        echo "Install homebrew and re-run this script"
    fi
    if [ "${HOMEBREW},${MACPORTS}" = "0,0" ]; then
        echo "Choose environment to install shoebot and depencencies:"
        echo "1. Homebrew [recommneded]"
        echo "2. Macports [unsupported]"
        echo "3. Exit"
        read -p ": " macenv
        if [ "$macenv" = "1" ]; then
          unset MACPORTS
        elif [ "$macenv" = "2" ]; then
          unset HOMEBREW
        else
          exit 1
        fi
    fi
        

    if [ "${HOMEBREW}" = "0" ]; then
        echo "Installing Shoebot dependencies on MacOSX Homebrew"
        brew install $HOMEBREW_PACKAGES
    fi

    if [ "${MACPORTS}" = "0" ]; then
        echo "Installing Shoebot dependencies on MacOSX macports"
        echo "This is unsupported, let us know if it works"                              
        sudo port install $MACPORTS_PACKAGES
    fi
    hash -r
}

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

if [ "Debian" = "$OS" ]; then
    install_debian
elif [ "LinuxMint" = "$OS" ]; then
    install_mint
elif [ "Ubuntu" = "$OS" ]; then
    install_ubuntu
elif [ "Redhat" = "$OS" ]; then
    install_redhat
elif [ "SuSE" = "$OS" ]; then
    install_suse
elif [ "Darwin" = "$OS" ]; then
    install_darwin
else
    if [ -z "$OS" ]; then
        echo $OS
    fi
    echo "Shoebot does not directly support $OS/$VER at the moment."
    echo ''
    echo 'Get started by looking at "Add support for another operating system".'
    echo 'in the installation documentation.'
    echo ''
fi
