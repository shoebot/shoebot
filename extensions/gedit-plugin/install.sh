#!/bin/sh

if [ -d '~/.gnome2/gedit/plugins' ]; then
  cp shoebotit* ~/.gnome2/gedit/plugins
  echo 'Gedit plugin successfully installed!'
else
  echo 'Local Gedit plugin directory does not exist. Creating it.'
  mkdir -p ~/.gnome2/gedit/plugins
  cp shoebotit* ~/.gnome2/gedit/plugins
  echo 'Gedit plugin successfully installed!'
fi

