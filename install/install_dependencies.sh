#!/bin/bash

REDHAT_PACKAGES="libjpeg-devel pycairo pygtk2 pygobject2 gnome-python2-rsvg python-imaging"
SUSE_PACKAGES="libjpeg-devel python-pycairo python-gtk python-pygobject2 python-rsvg python-imaging"

DEBIAN_PACKAGES="python2.7-dev libjpeg-dev python-cairo python-gtk2 python-gobject python-gtksourceview2 python-rsvg"
UBUNTU_PACKAGES="libjpeg-dev python-cairo python-gtk2 python-gobject python-gtksourceview2 python-rsvg"


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
elif [ "Ubuntu" = "$OS" ]; then
    install_ubuntu
elif [ "Redgat" = "$OS" ]; then
    install_redhat
elif [ "SuSE" = "$OS" ]; then
    install_suse
else
    echo TODO Add code for $OS
fi


