#!/usr/bin/env python

'''
Shoebox console runner

Copyright 2007, 2008 Ricardo Lafuente 
Developed at the Piet Zwart Institute, Rotterdam

This file is part of Shoebox.
'''

import sys
import os
import cairo

import shoebox

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
 
    infile = sys.argv[1]
    outfile = sys.argv[2]
    
    if len(sys.argv) == 5:
        width = sys.argv[3]
        height = sys.argv[4]
        box = shoebox.Box(outfile,width,height)
        box.run(infile)
        box.finish()
    elif len(sys.argv) == 3:
        box = shoebox.Box(outfile)
    else:
        usage("Wrong arguments")

