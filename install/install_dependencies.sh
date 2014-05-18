#!/bin/bash

install_debian() {
    sudo apt-get install python2.7-dev libjpeg-dev python-cairo python-gtk2 python-gobject python-gtksourceview2 python-rsvg
}

install_ubuntu() {
    sudo apt-get install libjpeg-dev python-cairo python-gtk2 python-gobject python-gtksourceview2 python-rsvg
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
    # TODO add code for Red Hat and CentOS here
    echo 'TODO - Add redhat/centos support'
else
    OS=$(uname -s)
    VER=$(uname -r)
fi



if [ "Debian" = "$OS" ]; then
    install_debian
elif [ "Ubuntu" = "$OS" ]; then
    install_ubuntu
else
    echo TODO Add code for $OS
fi


