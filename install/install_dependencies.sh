#!/bin/bash

# Linux
REDHAT_PACKAGES="libjpeg-devel pycairo pygtk2 pygobject2 gnome-python2-rsvg python-imaging"
SUSE_PACKAGES="libjpeg-devel python-pycairo python-gtk python-pygobject2 python-rsvg python-imaging"

DEBIAN_PACKAGES="python2.7-dev libjpeg-dev python-cairo python-gtk2 python-gobject python-gtksourceview3 python-rsvg"
UBUNTU_PACKAGES="libjpeg-dev python-cairo python-gtk2 python-gobject python-gtksourceview3 python-rsvg"
MINT_PACKAGES="python2.7-dev libjpeg-dev python-cairo python-gtk2 python-gobject python-gtksourceview3 python-rsvg"

# OSX
HOMEBREW_PACKAGES="cairo --quartz pango --quartz gtk+ --quartz pygtk --quartz"
MACPORTS_PACKAGES="cairo +quartz +no_x11 pango +quartz py27-pygtk +quartz +no_x11"

confirm() {
    read -p "Y/N" -n 1 -r
    echo     #
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

install_mint() {
    sudo apt-get install ${MINT_PACKAGES}
}

install_debian() {
    sudo apt-get install ${DEBIAN_PACKAGES}
}

install_ubuntu() {
    sudo apt-get install ${UBUNTU_PACKAGES}
}

install_redhat() {
    sudo yum install ${REDHAT_PACKAGES}
}

install_suse() {
    sudo zypper install ${SUSE_PACKAGES}
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

