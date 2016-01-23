# -*- coding: utf-8 -*-
"""
    The Pygments reStructuredText directive
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This fragment is a Docutils_ 0.5 directive that renders source code
    (to HTML only, currently) via Pygments.

    To use it, adjust the options below and copy the code into a module
    that you import on initialization.  The code then automatically
    registers a ``sourcecode`` directive that you can use instead of
    normal code blocks like this::

        .. sourcecode:: python

            My code goes here.

    If you want to have different code styles, e.g. one with line numbers
    and one without, add formatters with their names in the VARIANTS dict
    below.  You can invoke them instead of the DEFAULT one by using a
    directive option::

        .. sourcecode:: python
            :linenos:

            My code goes here.

    Look at the `directive documentation`_ to get all the gory details.

    .. _Docutils: http://docutils.sf.net/
    .. _directive documentation:
       http://docutils.sourceforge.net/docs/howto/rst-directives.html

    :copyright: Copyright 2006-2009 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

# Options
# ~~~~~~~

# Set to True if you want inline CSS styles instead of classes
INLINESTYLES = False

from pygments.formatters import HtmlFormatter

# The default formatter
DEFAULT = HtmlFormatter(noclasses=INLINESTYLES)

# Add name -> formatter pairs for every variant you want to use
VARIANTS = {
    'linenos': HtmlFormatter(noclasses=INLINESTYLES, linenos=True),
    'snapshot': str,
    'source': str,
}

BOT_HEADER = """
size(100, 100)
background(1)
fill(.95,.75,0)
"""

import os

from docutils import nodes
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from sphinx.errors import SphinxError
from sphinx.util import ensuredir, relative_uri

try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

import subprocess

def get_hashid(text,options):
    hashkey = text.encode('utf-8') + str(options)
    hashid = sha(hashkey).hexdigest()
    return hashid


class ShoebotError(SphinxError):
    category = 'shoebot error'


def html_img_tag(src):
    return '<img src="_static/{}">'.format(src)

class ShoebotDirective(Directive):
    """ Source code syntax hightlighting.
    """
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = dict([(key, directives.flag) for key in VARIANTS])
    has_content = True

    def run(self):
        self.assert_has_content()

        text = '\n'.join(self.content)
        parsed = highlight(text, PythonLexer(), HtmlFormatter())

        result = [nodes.raw('', parsed, format='html')]
        
        if True:  # If we want a snapshot - this should check the 'snapshot argument'# 
            fn = '{}.png'.format(sha(text).hexdigest())
            
            env = self.state.document.settings.env
            rel_filename, filename = env.relfn2path(fn)

            outfn = os.path.join(env.app.builder.outdir, '_static', rel_filename)
            ensuredir(os.path.dirname(outfn))
            script_to_render = BOT_HEADER + text
            try:
                subprocess.call(['sbot', '-o', '%s' % outfn, script_to_render])
            except Exception, e:
                raise ShoebotError(str(e))


            # TODO - Support other output formats
            image_node = nodes.raw('', html_img_tag(rel_filename), format='html')
            result.insert(0,image_node)
        
        return result



def setup(app):
    pass

directives.register_directive('shoebot', ShoebotDirective)
