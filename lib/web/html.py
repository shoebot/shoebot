### HTML #############################################################################################
# Code for stripping tags and collapsing whitespace.

# Author: Tom De Smedt.
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

import sgmllib
import re
from html.entities import name2codepoint
from .BeautifulSoup import UnicodeDammit

def clear_cache():
    Cache("html").clear()

#### REPLACE ENTITIES ################################################################################

# Windows-1252 is a character encoding of the Latin alphabet, 
# used by default in the legacy components of Microsoft Windows.
# List taken from Mark Pilgrim's feedparser.py
cp1252 = {
  chr(128): chr(8364), # euro sign
  chr(130): chr(8218), # single low-9 quotation mark
  chr(131): chr( 402), # latin small letter f with hook
  chr(132): chr(8222), # double low-9 quotation mark
  chr(133): chr(8230), # horizontal ellipsis
  chr(134): chr(8224), # dagger
  chr(135): chr(8225), # double dagger
  chr(136): chr( 710), # modifier letter circumflex accent
  chr(137): chr(8240), # per mille sign
  chr(138): chr( 352), # latin capital letter s with caron
  chr(139): chr(8249), # single left-pointing angle quotation mark
  chr(140): chr( 338), # latin capital ligature oe
  chr(142): chr( 381), # latin capital letter z with caron
  chr(145): chr(8216), # left single quotation mark
  chr(146): chr(8217), # right single quotation mark
  chr(147): chr(8220), # left double quotation mark
  chr(148): chr(8221), # right double quotation mark
  chr(149): chr(8226), # bullet
  chr(150): chr(8211), # en dash
  chr(151): chr(8212), # em dash
  chr(152): chr( 732), # small tilde
  chr(153): chr(8482), # trade mark sign
  chr(154): chr( 353), # latin small letter s with caron
  chr(155): chr(8250), # single right-pointing angle quotation mark
  chr(156): chr( 339), # latin small ligature oe
  chr(158): chr( 382), # latin small letter z with caron
  chr(159): chr( 376)  # latin capital letter y with diaeresis
}

def replace_entities(ustring, placeholder=" "):

    """Replaces HTML special characters by readable characters.

    As taken from Leif K-Brooks algorithm on:
    http://groups-beta.google.com/group/comp.lang.python
    
    """

    def _repl_func(match):
        try:
            if match.group(1): # Numeric character reference
                return chr( int(match.group(2)) ) 
            else:
                try: return cp1252[ chr(int(match.group(3))) ].strip()
                except: return chr( name2codepoint[match.group(3)] )
        except:
            return placeholder

    # Force to Unicode.
    if not isinstance(ustring, str):
        ustring = UnicodeDammit(ustring).str
    
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