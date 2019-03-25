#!/bin/bash

# Linux
REDHAT_PACKAGES="redhat-rpm-config gcc cairo-devel libjpeg-devel pycairo python2-gobject cairo-gobject python2-pillow"
# Fedora == Redhat, these are not detected separately.

SUSE_PACKAGES="gcc libjpeg62-devel python-pycairo python2-gobject python2-gobject-cairo python2-Pillow"

DEB_PACKAGES="build-essential libjpeg-dev python-cairo python2.7-dev python-gi-cairo python-gobject gir1.2-rsvg-2.0"
DEBIAN_PACKAGES=${DEB_PACKAGES}
UBUNTU_PACKAGES=${DEB_PACKAGES}
MINT_PACKAGES=${DEB_PACKAGES}


# OSX
HOMEBREW_PACKAGES="gtk+3 pygobject jpeg librsvg"
MACPORTS_PACKAGES="gtk3 cairo cairo-devel gobject-introspection py27-gobject jpeg librsvg"

confirm() {
    read -p "Y/N" -n 1 -r
    echo     #
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

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

    command -v brew
    HOMEBREW=$? > /dev/null

    echo 'Install on OSX...'
    echo brew ${HOMEBREW}
    echo port ${MACPORTS}

    if [ "${HOMEBREW}" = "0" ]; then
        echo Install using homebrew ?
        confirm
        #source ${DIR}/OSX/homebrew/install_dependencies.sh
        brew install $HOMEBREW_PACKAGES
    fi

    if [ "${MACPORTS}" = "0" ]; then
        echo Install using macports ?
        echo - Warning - sets the default python to python27 - !
        confirm
        sudo port install python27 py27-pip py27-virtualenv
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
