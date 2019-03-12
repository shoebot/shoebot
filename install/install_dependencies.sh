#!/bin/bash

# Linux
REDHAT_PACKAGES="libjpeg-devel pycairo pygtk2 pygobject2 gnome-python2-rsvg python-imaging"
SUSE_PACKAGES="libjpeg-devel python-pycairo python-gtk python-pygobject2 python-rsvg python-imaging"

DEB_PACKAGES="build-essential libjpeg-dev python-cairo python2.7-dev python-gi-cairo python-gobject"
OPTIONAL_DEB_PACKAGES="python-rsvg"

DEBIAN_PACKAGES=${DEB_PACKAGES}
OPTIONAL_DEBIAN_PACKAGES=${OPTIONAL_DEB_PACKAGES}

UBUNTU_PACKAGES=${DEB_PACKAGES}
OPTIONAL_UBUNTU_PACKAGES=${OPTIONAL_DEB_PACKAGES}

MINT_PACKAGES="python2.7-dev libjpeg-dev python-cairo python-gobject"
OPTIONAL_MINT_PACKAGES=${OPTIONAL_DEB_PACKAGES}

# OSX
HOMEBREW_PACKAGES="cairo --quartz pango --quartz gtk+3 --quartz pygobject3"
MACPORTS_PACKAGES="cairo +quartz +no_x11 pango +quartz py27-pygtk +quartz +no_x11"

confirm() {
    read -p "Y/N" -n 1 -r
    echo     #
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

deb_install() {
    # $0 packages
    # $1 optional packages
    sudo apt-get install -y $1
    if [ -z "$1" ]; then
        exit
    fi
    sudo apt-get install -y $2
    hash -r
}

install_mint() {
    deb_install "$MINT_PACKAGES" "$OPTIONAL_DEBIAN_PACKAGES"
}

install_debian() {
    deb_install "$DEBIAN_PACKAGES" "$OPTIONAL_DEBIAN_PACKAGES"
}

install_ubuntu() {
    deb_install "$UBUNTU_PACKAGES" "$OPTIONAL_UBUNTU_PACKAGES"
}

install_redhat() {
    sudo yum install "$REDHAT_PACKAGES"
    hash -r
}

install_suse() {
    sudo zypper install "$SUSE_PACKAGES"
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
    echo TODO Add code for $OS
fi
