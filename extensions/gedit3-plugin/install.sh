#!/bin/bash
~/.local/share/gedit/plugins

function pluginInstall {
  cp -r -f shoebotit* ~/.local/share/gedit/plugins
  echo 'Gedit plugin installed!'
}

function installLangSpecs {
  cp -f shoebot.lang ~/.local/share/gtksourceview-3.0/language-specs
  echo 'GTKSourceView language specs installed!'
}

if [ -d ~/.gnome2/gedit/plugins ]; then
  pluginInstall
else
  echo 'Local Gedit plugin directory does not exist. Creating it.'
  mkdir -p ~/.local/share/gedit/plugins
  pluginInstall
fi

if [ -d ~/.local/share/gtksourceview-3.0/language-specs ]; then
  installLangSpecs
else
  echo 'Local GTKSourceView language-specs directory does not exist. Creating it.'
  mkdir -p ~/.local/share/gtksourceview-3.0/language-specs
  installLangSpecs
fi

echo "All done, enable the shoebotit plugin on gedit's plugin menu"
