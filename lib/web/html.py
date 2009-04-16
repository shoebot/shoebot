### HTML #############################################################################################
# Code for stripping tags and collapsing whitespace.

# Author: Tom De Smedt.
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

import sgmllib
import re
from htmlentitydefs import name2codepoint
from BeautifulSoup import UnicodeDammit

def clear_cache():
    Cache("html").clear()

#### REPLACE ENTITIES ################################################################################

# Windows-1252 is a character encoding of the Latin alphabet, 
# used by default in the legacy components of Microsoft Windows.
# List taken from Mark Pilgrim's feedparser.py
cp1252 = {
  unichr(128): unichr(8364), # euro sign
  unichr(130): unichr(8218), # single low-9 quotation mark
  unichr(131): unichr( 402), # latin small letter f with hook
  unichr(132): unichr(8222), # double low-9 quotation mark
  unichr(133): unichr(8230), # horizontal ellipsis
  unichr(134): unichr(8224), # dagger
  unichr(135): unichr(8225), # double dagger
  unichr(136): unichr( 710), # modifier letter circumflex accent
  unichr(137): unichr(8240), # per mille sign
  unichr(138): unichr( 352), # latin capital letter s with caron
  unichr(139): unichr(8249), # single left-pointing angle quotation mark
  unichr(140): unichr( 338), # latin capital ligature oe
  unichr(142): unichr( 381), # latin capital letter z with caron
  unichr(145): unichr(8216), # left single quotation mark
  unichr(146): unichr(8217), # right single quotation mark
  unichr(147): unichr(8220), # left double quotation mark
  unichr(148): unichr(8221), # right double quotation mark
  unichr(149): unichr(8226), # bullet
  unichr(150): unichr(8211), # en dash
  unichr(151): unichr(8212), # em dash
  unichr(152): unichr( 732), # small tilde
  unichr(153): unichr(8482), # trade mark sign
  unichr(154): unichr( 353), # latin small letter s with caron
  unichr(155): unichr(8250), # single right-pointing angle quotation mark
  unichr(156): unichr( 339), # latin small ligature oe
  unichr(158): unichr( 382), # latin small letter z with caron
  unichr(159): unichr( 376)  # latin capital letter y with diaeresis
}

def replace_entities(ustring, placeholder=" "):

    """Replaces HTML special characters by readable characters.

    As taken from Leif K-Brooks algorithm on:
    http://groups-beta.google.com/group/comp.lang.python
    
    """

    def _repl_func(match):
        try:
            if match.group(1): # Numeric character reference
                return unichr( int(match.group(2)) ) 
            else:
                try: return cp1252[ unichr(int(match.group(3))) ].strip()
                except: return unichr( name2codepoint[match.group(3)] )
        except:
            return placeholder

    # Force to Unicode.
    if not isinstance(ustring, unicode):
        ustring = UnicodeDammit(ustring).unicode
    
    # Don't want some weird unicode character here
    # that truncate_spaces() doesn't know of:
    ustring = ustring.replace("&nbsp;", " ")
    
    # The ^> makes sure nothing inside a tag (i.e. href with query arguments) gets processed.
    _entity_re = re.compile(r'&(?:(#)(\d+)|([^;^> ]+));') 
    return _entity_re.sub(_repl_func, ustring) 

#### STRIP TAGS ######################################################################################

class Tagstripper(sgmllib.SGMLParser):
    
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)

    def strip(self, html, exclude=[], linebreaks=False, blocks="\n", breaks="\n", columns="\n"):
	    self.data = ""
	    self.exclude = exclude
	    self.linebreaks = linebreaks
	    self.block = blocks
	    self.blocks = [
            "h1", "h2", "h3", "h4", "h5", "h6",
            "p", "center", "blockquote",
            "div", "table", "ul", "ol",
            "pre", "code", "form"
        ]
	    self.break_ = breaks
	    self.breaks = [
	       "br", "tr", "li"
	    ]
	    self.columns = columns
	    self.feed(self.prepare(html))
	    self.close()
	    return self.data
    
    def prepare(self, html):
        # Clean up faulty HTML before parsing.
        html = html.replace("<br/>", "<br />")
        html = html.replace("<hr/>", "<hr />")
        # Display list items with an asterisk.
        #html = html.replace("li>", "li>*")
        html = re.sub(r"<li.*?>", "\n<li>* ", html)
        #html = html.replace("li>\n", "li>")
        # Make sure there is a space between elements.
        html = html.replace("><", "> <")
        # Linebreaks in the source should not end up in the output.
        if not self.linebreaks:
        	html = html.replace("\r", "\n")
        	html = html.replace("\n", " ")
        return html
    
    def unknown_starttag(self, tag, attributes):
        # Include tags from the whitelist in the output.
        if tag in self.exclude:
            self.data += "<"+tag+">"
        # Add linebreaks before and after block-level elements.
        if tag in self.blocks:
            self.data += self.block
        # Convert things like <tr> and <br /> to linebreak.
        if tag in self.breaks:
            self.data += self.break_
    
    def unknown_endtag(self, tag):
        # Close tags from the whitelist in the output.
        if tag in self.exclude:
            self.data += "</"+tag+">"
        # Add linebreaks before and after block-level elements.
        if tag in self.blocks:
            self.data += self.block
        # Usually it's cleaner to separate columns by linebreaks too.
        if tag == "td":
            self.data += self.columns

    def handle_data(self, data):
	    self.data += data
	
    def handle_entityref(self, ref):
        # Let entity refs (e.g. &nbsp;) pass.
        self.data += "&"+ref+";"
        
    def handle_charref(self, ref):
        # Let things like &#405; pass.
        self.data += "&"+ref+";"
	
def strip_tags(html, exclude=[], linebreaks=False, blocks="\n", breaks="\n", columns="\n"):
    # Removes all tags from HTML except those in the whitelist.
    # This can leave a clutter of javascript and whitespace.
    return Tagstripper().strip(html, exclude, blocks, breaks, columns)

#### STRIP CODE AND COMMENTS #########################################################################

def strip_between(start, end, str):
    # ? denotes non-greedy *
    # The dot matches anything in this pattern, including linebreaks.
    # Replace is case-incensitive.
    p = re.compile(r""+start+".*?"+end, re.DOTALL | re.I)
    return re.sub(p, "", str)

def strip_javascript(html):
    return strip_between("<script", "</script>", html)

def strip_inline_css(html):
    return strip_between("<style", "</style>", html)
    
def strip_comments(html):
    return strip_between("<!--", "-->", html)
    
def strip_forms(html):
    return strip_between("<form", "</form>", html)

#### COLLAPSE WHITESPACE #############################################################################

def collapse_spaces(str):
    # If there are 10 consecutive spaces, 9 of them are removed.
    # Tabs not at the beginning of a line are truncated as well, e.g "this      is untidy".
    #str = re.sub(r"[[^$\t]\t]+", " ", str)
    str = re.sub(r"[ ]+", " ", str).strip(" ")
    return str

def collapse_linebreaks(str, max=2):
    # Allow only a maximum of max linebreaks to build up,
    # stripping additional whitespace lines from the output.
    lines = str.split("\n")
    str = ""
    i = 0
    for l in lines:
        if l.strip() == "":
            i += 1
        else:
            i = 0
        if i < max:
            str += l.strip(" ")
            str += "\n"
    return str.strip()
    
def collapse_tabs(str, indent=False):
    # Converts tabs to spaces, optionally leaving the left indentation unmodified.
    # collapse_spaces() should be called after this.
    if not indent:
        return str.replace("\t", " ")
    else:
        p = re.compile(r"^(\t+)", re.MULTILINE)
        delimiter = "$$$_INDENTATION"
        str = re.sub(p, "\\1"+delimiter, str)
        lines = str.split("\n")
        str = ""
        for l in lines:
            i = l.find(delimiter)
            #if i >= 0:
            l = l[:i] + l[i:].replace("\t", " ")
            str += l + "\n"
        str = str.replace(delimiter, "")
        return str
        
def plain(html):
	
	try: html = str(html)
	except:
		pass
	
	if html == "None": html = ""
	html = strip_javascript(html)
	html = strip_inline_css(html)
	html = strip_comments(html)
	html = strip_forms(html)
	html = strip_tags(html, columns="")
	html = replace_entities(html)
	html = collapse_tabs(html)
	html = collapse_spaces(html)
	html = collapse_linebreaks(html)	
	
	return html

#from urllib import urlopen
#html = urlopen("http://nodebox.net").read()
#print html
#print "##############################################"
#print plain(html)