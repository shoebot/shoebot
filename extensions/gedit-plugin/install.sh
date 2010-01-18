#!/bin/sh

if [ -d ~/.gnome2/gedit/plugins ]; then
  cp -f shoebotit* ~/.gnome2/gedit/plugins
  echo 'Gedit plugin successfully installed!'
else
  echo 'Local Gedit plugin directory does not exist. Creating it.'
  mkdir -p ~/.gnome2/gedit/plugins
  cp -f shoebotit* ~/.gnome2/gedit/plugins
  echo 'Gedit plugin successfully installed!'
fi

if [ -d ~/.gnome2/gtksourceview-1.0/language-specs ]; then
  cp -f shoebot.lang ~/.gnome2/gtksourceview-1.0/language-specs
  echo 'GTKSourceView language specs successfully installed!'
else
  echo 'Local GTKSourceView language-specs directory does not exist. Creating it.'
  mkdir -p ~/.gnome2/gtksourceview-1.0/language-specs
  cp -f shoebot.lang ~/.gnome2/gtksourceview-1.0/language-specs
  echo 'GTKSourceView language specs successfully installed!'
fi


