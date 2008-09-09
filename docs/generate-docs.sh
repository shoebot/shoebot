#!/bin/bash

# Generate PyDoc documentation for the Shoebot module.

# TODO: Check if epydoc is installed

CURRENT_DIR=`pwd`

mkdir pydoc
cd ..
epydoc shoebot \
	--output=docs/pydoc \
	--html \
	--show-imports \
	--name=shoebot \
	--verbose \
	
	

