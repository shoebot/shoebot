# Shoebot

Shoebot is a creative coding environment designed for making vector graphics and
animations with Python. It's geared towards playful graphic exploration,
creating SVG images for pen plotters, and is a great tool for automated/headless
image generation.

[![Build Status](https://github.com/shoebot/shoebot/actions/workflows/test.yml/badge.svg)](https://github.com/shoebot/shoebot/actions/workflows/test.yml)
[![Matrix channel](https://img.shields.io/matrix/shoebot:matrix.org)](https://matrix.to/#/#shoebot:matrix.org)

Shoebot takes a Python script describing a drawing process, and outputs a
graphic in vector (SVG, PDF, PostScript) and bitmap formats (PNG). Animations
can be easily created and output to video files (mp4). Scripts can describe
their own GUIs for [controlling variables
interactively](https://docs.shoebot.net/live.html). Shoebot can also be run from
the commandline and [used as a Python
module](https://docs.shoebot.net/advanced.html#using-shoebot-as-a-python-module)
inside other Python scripts.

Shoebot is a port/rewrite of [Nodebox
1](http://nodebox.net/code/index.php/Home), which is derived from
[DrawBot](http://drawbot.com). The playful coding philosophy of
[Shoes](http://shoesrb.com/)  also inspired its development. Thus, "Shoebot".   

* [How to install](https://docs.shoebot.net/install.html)
* [Getting started](https://docs.shoebot.net/getstarted.html)

## Documentation

The Shoebot Manual can be found at [docs.shoebot.net](https://docs.shoebot.net/).

## Getting help

Installation is the trickiest aspect of Shoebot. If you run into trouble
following the [install steps](https://docs.shoebot.net/install.html), create a
[new issue](https://github.com/shoebot/shoebot/issues/new) and paste the output
of the following commands:

    python3 setup.py diagnose
    python3 setup.py test

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

Copyright &copy; 2007-2021 The Shoebot authors (Stuart Axon, Dave Crossland,
Francesco Fantoni, Ricardo Lafuente, Sebastian Oliva)

Originally developed by Ricardo Lafuente with the support of the Piet Zwart
Institute, Rotterdam.

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
