#!/bin/bash

if [ "$USER" = "root" ]; then
  SHARE_DIR="/usr/share"
  echo Install locally to $SHARE_DIR
else
  SHARE_DIR="$HOME/.local/share"
  echo Install globally to $SHARE_DIR
fi

function pluginInstall {
  cp -r -f shoebotit* $SHARE_DIR/gedit/plugins
  echo 'Gedit plugin installed!'
}

function installLangSpecs {
  cp -f shoebot.lang $SHARE_DIR/gtksourceview-3.0/language-specs
  update-mime-database $SHARE_DIR/mime
  echo 'GTKSourceView language specs installed!'
}

if [ -d $SHARE_DIR/gedit/plugins ]; then
  pluginInstall
else
  echo 'Local Gedit plugin directory does not exist. Creating it.'
  mkdir -p $SHARE_DIR/gedit/plugins
  pluginInstall
fi

if [ -d $SHARE_DIR/gtksourceview-3.0/language-specs ]; then
  installLangSpecs
else
  echo 'Local GTKSourceView language-specs directory does not exist. Creating it.'
  mkdir -p $SHARE_DIR/gtksourceview-3.0/language-specs
  installLangSpecs
fi

echo "All done, enable the shoebotit plugin on gedit's plugin menu"
