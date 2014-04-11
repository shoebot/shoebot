#!/bin/bash

if [ "$USER" = "root" ]; then
  if [ -d "/usr/lib64" ]; then
    DEST_DIR="/usr/lib64"
  else
    DEST_DIR="/usr/lib"
  fi
  echo Install globally to $DEST_DIR
else
  DEST_DIR="$HOME/.local/share"
  echo Install locally to $DEST_DIR
fi

function pluginInstall {
  cp -r -f shoebotit* $DEST_DIR/gedit/plugins
  echo 'Gedit plugin installed!'
}

function installLangSpecs {
  cp -f shoebot.lang $DEST_DIR/gtksourceview-3.0/language-specs
  update-mime-database $DEST_DIR/mime
  echo 'GTKSourceView language specs installed!'
}

if [ -d $DEST_DIR/gedit/plugins ]; then
  pluginInstall
else
  echo 'Local Gedit plugin directory does not exist. Creating it.'
  mkdir -p $DEST_DIR/gedit/plugins
  pluginInstall
fi

if [ -d $DEST_DIR/gtksourceview-3.0/language-specs ]; then
  installLangSpecs
else
  echo 'Local GTKSourceView language-specs directory does not exist. Creating it.'
  mkdir -p $DEST_DIR/gtksourceview-3.0/language-specs
  installLangSpecs
fi

echo "All done, enable the shoebotit plugin on gedit's plugin menu"
