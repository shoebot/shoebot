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
    image will be 400x400 px (bitmap) or 400x400 points (vector).

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
    # check number of args
    # 5 args = width and height were specified
    if len(sys.argv) == 5:
        width = sys.argv[3]
        height = sys.argv[4]
        box = shoebox.Box(outfile,width,height)
        box.run(infile)
        box.finish()
    # 3 args = defaul
    elif len(sys.argv) == 3:
        box = shoebox.Box(outfile,400,400)
        box.run(infile)
        box.finish()
    else:
        usage("Wrong arguments")

