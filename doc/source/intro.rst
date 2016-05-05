Introduction
============

Shoebot is a tool to automate the process of drawing vector graphics using a
minimal and easy-to-understand syntax.

Using code to create and tweak shapes, colours and features is a model that
departs from the WYSIWYG paradigm that is present in mainstream graphics
applications. Shoebot was inspired by a rich lineage of tools dedicated to
generative creativity:

  * Nodebox
  * Drawbot
  * Processing
  * Paper.js
  * Scriptographer
  * Design By Numbers

Shoebot is a fork/rewrite of `Nodebox 1
<https://www.nodebox.net/code/index.php/Home>`_, which is itself based on
`DrawBot <http://www.drawbot.com/>`_. There are slightly different syntax
approaches in each language, and Shoebot tries to support both.


Why scripting?
--------------

The most evident purpose of scripting is to automate repetitive
tasks; for example, one could create an image with 2000 randomly positioned
circles with two lines of code:

.. shoebot::
    :snapshot:
    :size: 400, 400

    for step in range(2000):
        ellipse(random(WIDTH), random(HEIGHT), 10, 10)
      
This is something that would be much more involved to create using the
mouse and keyboard to draw on the canvas manually. Using scripts to control
your output offers many new uses and possibilities for image generation and
manipulation. 

One common use for this kind of approach is the creation of dynamic systems to
generate drawings, be them 'generative' (systems that grow, often
unpredictably, from a set of initial parameters) or 'procedural' (rule-based
systems).


Why use Shoebot
---------------

Shoebot is meant to run scripts with instructions to draw both simple shapes
and complex compositions. The syntax is Python with a set of additional
commands that ease the process of iterating through different options and
designs. There are many examples showcasing the possibilities of Shoebot inside
the ``examples/`` directory.

The output of Shoebot scripts can be exported to the most widely used vector
file formats -- SVG, PDF and PostScript -- as well as the PNG bitmap
format.

Shoebot's distinguishing feature is that it can be run in a terminal without a
graphical editor. Drawing without the overhead of a GUI makes Shoebot a useful
and easy-to-grasp tool for fast, procedural image generation.

A script's variables can be accessed through an automatically generated GUI or
even from outside applications -- see the :doc:`interfacing` section.

There is also a set of libraries ported from Nodebox which enable SVG
importing, Spiro splines, image fetching and manipulation, computer vision,
video and webcam input, and more!

