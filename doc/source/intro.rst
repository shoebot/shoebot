Introduction
============

Shoebot is, simply put, an application for the purpose of scripting pictures. In
case you're familiar with the 'sketch' approach of Processing and Nodebox, you
can skip over to the ___ section.

Using code to create and tweak shapes, colours and features is a model that
departs from the WYSIWYG paradigm that is present in applications like GIMP and
Inkscape (Adobe Photoshop and Illustrator being the proprietary alternatives).
The most evident purpose of scripting is to automate repetitive tasks; for
example, one could create an image with 2000 randomly positioned circles with
two lines of code:

  for step in range(2000):
      ellipse(random(WIDTH), random(HEIGHT), 10, 10)
      
This is something that you'd find a bit more convoluted to create using your
mouse and keyboard to draw on the canvas manually. While the GUI editing
applications certainly have many upsides to them, using scripts to control
your output offers many new uses and possibilities for image generation and
manipulation. 

One common use for this kind of approach is the creation of dynamic systems
to generate drawings, be them 'generative' (systems that grow, often
unpredictably, from a set of initial parameters) or 'procedural' (systems...)

Capabilities
------------

The output of Shoebot scripts can be exported to a few vector file formats --
SVG, Postscript (.ps) and PDF -- as well as the PNG bitmap format.

A script's variables can be accessed through an automatically generated GUI or
even from outside applications (see the ___ section).

There's many libraries ported from Nodebox which enable SVG importing, Spiro
splines, image fetching and manipulation and other goodies; there's also Shoebot
libraries to work with video and webcam input, along with computer vision (OpenCV).
