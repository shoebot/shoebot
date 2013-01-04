#!/bin/bash

function pluginInstall {
  cp -r -f shoebotit* ~/.gnome2/gedit/plugins
  echo 'Gedit plugin installed!'
}

function installLangSpecs {
  cp -f shoebot.lang ~/.gnome2/gtksourceview-1.0/language-specs
  echo 'GTKSourceView language specs installed!'
}

if [ -d ~/.gnome2/gedit/plugins ]; then
  pluginInstall
else
  echo 'Local Gedit plugin directory does not exist. Creating it.'
  mkdir -p ~/.gnome2/gedit/plugins
  pluginInstall
fi

if [ -d ~/.gnome2/gtksourceview-1.0/language-specs ]; then
  installLangSpecs
else
  echo 'Local GTKSourceView language-specs directory does not exist. Creating it.'
  mkdir -p ~/.gnome2/gtksourceview-1.0/language-specs
  installLangSpecs
fi

echo "All done, enable the shoebotit plugin on gedit's plugin menu"
