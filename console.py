#!/usr/bin/env python

'''
Shoebox console runner

Copyright 2007, 2008 Ricardo Lafuente 
Developed at the Piet Zwart Institute, Rotterdam

This file is part of Shoebox.

Shoebox is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Shoebox is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Shoebox.  If not, see <http://www.gnu.org/licenses/>.

Code parts were taken from Nodebox (http://www.nodebox.net),
Inkscape (http://www.inkscape.org), pyCairo 
(http://www.cairographics.org/pycairo) and other 
authors (credited in each module)
'''

import sys
import os
import cairo

import shoebox
from shoebox import util

class CodeRunnerError(Exception): pass

# supported formats
vectorformats = ["svg","ps","pdf"]
bitmapformats = ["png"]
supportedformats = vectorformats + bitmapformats 

class CodeRunner(object):
    def __init__(self):
        self.namespace = {}

    def run(self, infile, outfile, width=1000, height=1000):
        '''
        Run shoebox code from infile and create an image as outfile.
        Canvas size settings are also defined here.
        '''
        self.width = width
        self.height = height
        self.inputfilename = infile
        self.outputfilename = outfile
        print "Source file: " + infile
        print "Output image file: " + outfile
        print
        print "Width: " + str(width)
        print "Height: " + str(height)
        # create a Cairo surface
        self.surface = util.surfacefromfilename(self.outputfilename,self.width,self.height)
        # create the drawing context
        self.vec = shoebox.Box(self.surface, self.width, self.height)
        # and run the code
        self.vec.cairo.save()
        self.runexternalscript()
        self.vec.cairo.restore()
        # now we need to know the file extension
        ext = self.outputfilename[-3:]
        # if it's a vector surface (svg et al), just wrap up and finish
        if ext in vectorformats:
            self.vec.cairo.show_page()
            self.surface.finish()
        # but bitmap surfaces need us to tell them to save to a file
        else:
            self.surface.write_to_png(self.outputfilename)
            print self.outputfilename

    def quickrun(self):
        pass

    def runexternalscript(self):
        # make the namespace in which the script should be run
        self._initNamespace(self.vec)
        # save the Cairo context state (not sure this is needed, but heck)
        self.vec.cairo.save()
        # get the file contents
        file = open(self.inputfilename, 'rU')
        source_or_code = file.read()
        file.close()
        # now run the code
        try:
            # if it's a string, it needs compiling first; if it's a file, no action needed
            if isinstance(source_or_code, basestring):
                source_or_code = compile(source_or_code + "\n\n", "<Untitled>", "exec")
            # do the Cairo magic
            #exec source_or_code in self.namespace
            exec source_or_code in self.namespace
        except:
            # something went wrong; print verbose system output
            # maybe this is too verbose, but okay for now
            print sys.exc_info()
            exc_type, exc_value = sys.exc_info()[:2]
            print >> sys.stderr, exc_type, exc_value
        else:
            # finish by restoring the Cairo context state
            self.vec.cairo.restore()

    def _initNamespace(self, context, frame=1):
        self.namespace.clear()
        # Add everything from the util namespace
        for name in dir(util):
            self.namespace[name] = getattr(util, name)
        # Add everything from our context object (includes the 
        # Cairo context and Nodebox commands)
        for name in dir(context):
            self.namespace[name] = getattr(context, name)

        # Add the document global
        #self.namespace["__doc__"] = self.__doc__

        # Add the frame
        #self.frame = frame
        #self.namespace["PAGENUM"] = self.namespace["FRAME"] = self.frame

def usage(err=""):
    if len(err) > 0:
        err = '\n\nError: ' + str(err)
    print """Shoebox console runner

    Usage: python console.py <sourcefile> <imagefile> [<width> <height>]
    width and height are optional values; if not specified, the resulting
    image will be 1000x1000px (bitmap) or 1000x1000 points (vector).

    Supported vector image extensions: pdf, svg, ps
    Supported bitmap image extensions: png
    """ + err
    sys.exit()

if __name__ == '__main__':
    verbose = True
    debug = False
    if sys.argv[1] == '-h':
        usage()
    runner = CodeRunner()
    infile = sys.argv[1]
    outfile = sys.argv[2]
    if len(sys.argv) == 5:
        width = sys.argv[3]
        height = sys.argv[4]
        runner.run(infile,outfile,width,height)
    elif len(sys.argv) == 3:
        runner.run(infile,outfile)
    else:
        usage("Wrong arguments")

