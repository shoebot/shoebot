#!/usr/bin/env python3

# This file is part of Shoebot.
# Copyright (C) 2007-2009 the Shoebot authors
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

import typing
from contextlib import contextmanager

from shoebot.graphics import BezierPath


class Canvas:
    def __init__(self, output, extents: typing.Optional[typing.Tuple[float, float, float, float]] = None, resizable=None, speed=None, **kwargs):
        """
        :param extents: Extents of recording surface, or None for unbounded.
        :param resizable: If True, the surface will be resizable.
        """

        # TODO - maybe some of these will move into the Context State too
        self.commands: typing.List[typing.Tuple[typing.Grob, typing.Dict]] = []
        self.clip_stack  = []
        self.clip_path = None

        # TODO - are these parameters correct (not exactly - separate these into categories of what they are)
        self.resizable = resizable or extents is None
        self.output = output
        self.realised_size = None

        self.position = (0, 0)
        self.speed = speed

        # TODO fixup these state variables
        # State temporarily here to get to "first rectangle" - this needs moving into the context
        # (e.g. Grammar)
        # self.width = None
        # self.height = None
        #
        # self.font = None
        # self.fontsize = None
        # self.fontweight = None
        # self.fontslant = None
        # self.fontvariant = None
        #
        # self.fillcolor = None
        # self.fillrule = None
        # self.strokerule = None
        # self.strokecolor = None
        # self.strokewidth = 1
        # self.strokecap = None
        # self.strokejoin = None
        # self.strokedash = None
        # self.dashoffset = None
        #
        # self.blendmode = None
        #
        # self.transform = None

    def set_size(self, *dimensions):
        # Size is known, so setup renderers if have not been already and render everything up to this point.
        print("set_size", dimensions)
        if self.realised_size is None:
            print("create renderer", self.output)
            self.output.create_renderer(*dimensions)
            self.realised_size = dimensions
        else:
            print("resize renderer - not supported")
            raise NotImplementedError("Resize not supported")

        self.width, self.height = dimensions
        return self.width, self.height  # TODO - is this correct?

    def draw_image(self, image):
        # TODO - do we need to freeze the state?
        self.commands.append((image, image.__state_stack__))

    def draw_path(self, path: BezierPath):
        # TODO - do we need to freeze the state?
        self.commands.append((path, path.__state_stack__))

    def translate(self, x, y):
        self.position = (x, y)  # TODO - this is not used by the renderer yet.

    def push_clip(self, path):
        # TODO
        self.clip_path = path
        self.clip_stack.push(path)

    def pop_clip(self):
        if self.clip_path is None:
            raise ValueError("No clip to pop")
        if len(self.clip_stack) == 0:
            self.clip_path = None
        else:
            self.clip_path = self.clip_stack.pop()

    @contextmanager
    def revertible(self):
        # TODO in future you may have multiple renderers
        with self.output.revertible():
            yield self

    @contextmanager
    def new_page(self, context):
        # TODO
        yield self



