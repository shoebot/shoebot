# Shoebot

Shoebot is a Python graphics robot: It takes a Python script as input, which describes a drawing process, and outputs a graphic in a common open standard format (SVG, PDF, PostScript, or PNG). It works through simple text files, and scripts can describe their own GUIs for controlling variables interactively. It can also be used as a Python module, a plugin for Python-scriptable tools such as Inkscape, and run from the command line. 

Shoebot is a port/rewrite of [Nodebox 1](http://nodebox.net/code/index.php/Home). It was also inspired by [DrawBot](http://drawbot.com) and [Shoes](http://shoesrb.com/). Thus, "Shoebot".

[![Build Status](https://travis-ci.org/shoebot/shoebot.svg?branch=master)](https://travis-ci.org/shoebot/shoebot)

* [How to install](http://shoebot.readthedocs.io/en/latest/install.html)
* [Getting started](http://shoebot.readthedocs.io/en/latest/commands.html) 

## Documentation

You can find the current docs at [ReadTheDocs](http://shoebot.readthedocs.org/).

The [Nodebox tutorials](http://nodebox.net/code/index.php/Tutorial) are an excellent intro to the language and its core concepts. Shoebot is a rewrite of Nodebox 1, so the original [Nodebox documentation](https://www.nodebox.net/code/index.php/Reference) is required reading.

The [Shoebot documentation](http://shoebot.readthedocs.org) has quite a lot more information on what you can do with Shoebot. Take a look at the [wiki](https://github.com/shoebot/shoebot/wiki) for a set of hacks and advanced uses such as:

  * import Shoebot as a Python module
  * use the included socketserver to have other programs control a Shoebot script
  * generate images via CGI scripts

## Getting help

Installation can sometimes be tricky, to help us work out whats up paste the output
of the following commands into an issue on github

    python setup.py diagnose
    python setup.py test

This will help us diagnose common issues more quickly.


Links
-----

  * [Website](http://shoebot.net)
  * [Documentation](http://shoebot.readthedocs.org)
  * [Mailing lists](http://tinkerhouse.net/shoebot/devel)
  * [Source code](http://github.com/shoebot/shoebot)
  * [Issue tracker](http://github.com/shoebot/shoebot/issues)


License
-------

Copyright &copy; 2007-2018 The Shoebot authors (Stuart Axon, Dave Crossland, Francesco Fantoni, Ricardo Lafuente, Sebastian Oliva)
Originally developed by Ricardo Lafuente with the support of the Piet Zwart Institute, Rotterdam.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


