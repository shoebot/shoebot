#!/usr/bin/env python3

# This file is part of Shoebot.
# Copyright (C) 2009 the Shoebot authors
# See the COPYING file for the full license text.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
#   WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#   MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Assorted utility functions, mainly for color and font handling"""


class ShoebotInstallError(Exception):
    pass


class UnbufferedFile:
    """
    File wrapper, that flushes on writes.

    http://stackoverflow.com/questions/230751/how-to-flush-output-of-python-print
    """

    def __init__(self, fd):
        self.fd = fd

    def write(self, x):
        self.fd.write(x)
        self.fd.flush()

    def writelines(self, lines):
        self.fd.writelines(lines)
        self.fd.flush()

    def flush(self):
        return self.fd.flush()

    def close(self):
        return self.fd.close()

    def fileno(self):
        return self.fd.fileno()


def _copy_attr(v):
    if v is None:
        return None
    elif hasattr(v, "copy"):
        return v.copy()
    elif isinstance(v, list):
        return list(v)
    elif isinstance(v, tuple):
        return tuple(v)
    elif isinstance(v, (int, str, float, bool)):
        return v
    else:
        raise ValueError(_("Don't know how to copy '%s'.") % v)


def _copy_attrs(source, target, attrs):
    """
    Copy attributes from source to target.

    :param source: source object
    :param target: destination object
    :param attrs: sequence of attributes to copy.
    :return:
    """
    for attr in attrs:
        setattr(target, attr, _copy_attr(getattr(source, attr)))
