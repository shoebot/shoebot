# coding: utf-8

### WIKIPEDIA ########################################################################################
# Code for querying Wikipedia and parsing articles.
# The parser is as-is, it handles a lot but not everything.

# Author: Tom De Smedt.
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

import re
from xml.dom import minidom
from urllib import quote

from url import URLAccumulator
from html import replace_entities, strip_tags
from cache import Cache
import mimetex

def clear_cache():
    Cache("wikipedia").clear()

### WIKIPEDIA PAGE MISSING ERROR #####################################################################

class WikipediaPageMissing(Exception):
    def __str__(self): return str(self.__class__)

### WIKIPEDIA LANGUAGES ##############################################################################

languages = {
    "aa"           : u"Afar",
    "ab"           : u"Abkhaz",
    "af"           : u"Afrikaans",
    "ak"           : u"Akan",
    "als"          : u"Alemannic",
    "am"           : u"Amharic",
    "an"           : u"Aragonese",
    "ang"          : u"Old English",
    "ar"           : u"Arabic",
    "arc"          : u"Aramaic",
    "as"           : u"Assamese",
    "ast"          : u"Asturian",
    "av"           : u"Avar",
    "ay"           : u"Aymara",
    "az"           : u"Azerbaijani",
    "ba"           : u"Bashkir",
    "bar"          : u"Bavarian",
    "bat-smg"      : u"Samogitian",
    "be"           : u"Belarusian",
    "bg"           : u"Bulgarian",
    "bh"           : u"Bihara",
    "bi"           : u"Bislama",
    "bm"           : u"Bambara",
    "bn"           : u"Bengali",
    "bo"           : u"Tibetan",
    "bpy"          : u"Bishnupriya Manipuri",
    "br"           : u"Breton",
    "bs"           : u"Bosnian",
    "bug"          : u"Buginese",
    "bxr"          : u"Buryat (Russia)",
    "ca"           : u"Catalan",
    "cbk-zam"      : u"Zamboanga Chavacano",
    "cdo"          : u"Min Dong",
    "ce"           : u"Chechen",
    "ceb"          : u"Cebuano",
    "ch"           : u"Chamorro",
    "cho"          : u"Choctaw",
    "chr"          : u"Cherokee",
    "chy"          : u"Cheyenne",
    "co"           : u"Corsican",
    "cr"           : u"Cree",
    "crh"          : u"Crimean Tatar",
    "crh-latn"     : u"Crimean Tatar (Latin)",
    "crh-cyrl"     : u"Crimean Tatar (Cyrillic)",
    "cs"           : u"Czech",
    "csb"          : u"Cassubian",
    "cu"           : u"Old Church Slavonic (ancient language)",
    "cv"           : u"Chuvash",
    "cy"           : u"Welsh",
    "da"           : u"Danish",
    "de"           : u"German",
    "diq"          : u"Zazaki",
    "dk"           : u"Danish",
    "dv"           : u"Dhivehi",
    "dz"           : u"Bhutani",
    "ee"           : u"Ewe",
    "el"           : u"Greek",
    "eml"          : u"Emilian-Romagnol/Sammarinese",
    "en"           : u"English",
    "eo"           : u"Esperanto",
    "es"           : u"Spanish",
    "et"           : u"Estonian",
    "eu"           : u"Basque",
    "fa"           : u"Persian",
    "ff"           : u"Fulah",
    "fi"           : u"Finnish",
    "fiu-vro"      : u"Voro",
    "fj"           : u"Fijian",
    "fo"           : u"Faroese",
    "fr"           : u"French",
    "frp"          : u"Franco-Provencal/Arpitan",
    "fur"          : u"Friulian",
    "fy"           : u"Frisian",
    "ga"           : u"Irish",
    "gd"           : u"Scots Gaelic",
    "gl"           : u"Gallegan",
    "glk"          : u"Gilaki",
    "gn"           : u"Guarani",
    "got"          : u"Gothic",
    "gsw"          : u"Alemannic",
    "gu"           : u"Gujarati",
    "gv"           : u"Manx",
    "ha"           : u"Hausa",
    "haw"          : u"Hawaiian",
    "he"           : u"Hebrew",
    "hi"           : u"Hindi",
    "hil"          : u"Hiligaynon",
    "ho"           : u"Hiri Motu",
    "hr"           : u"Croatian",
    "hsb"          : u"Upper Sorbian",
    "ht"           : u"Haitian",
    "hu"           : u"Hungarian",
    "hy"           : u"Armenian",
    "hz"           : u"Herero",
    "ia"           : u"Interlingua (IALA)",
    "id"           : u"Indonesian",
    "ie"           : u"Interlingue (Occidental)",
    "ig"           : u"Igbo",
    "ii"           : u"Sichuan Yi",
    "ik"           : u"Inupiak",
    "ilo"          : u"Ilokano",
    "io"           : u"Ido",
    "is"           : u"Icelandic",
    "it"           : u"Italian",
    "iu"           : u"Inuktitut",
    "ja"           : u"Japanese",
    "jbo"          : u"Lojban",
    "jv"           : u"Javanese",
    "ka"           : u"Georgian",
    "kaa"          : u"Karakalpak",
    "kab"          : u"Kabyle",
    "kg"           : u"KiKongo",
    "ki"           : u"Kikuyu",
    "kj"           : u"Kuanyama",
    "kk"           : u"Kazakh",
    "kk-cn"        : u"Kazakh Arabic",
    "kk-kz"        : u"Kazakh Cyrillic",
    "kk-tr"        : u"Kazakh Latin",
    "kl"           : u"Greenlandic",
    "km"           : u"Cambodian",
    "kn"           : u"Kannada",
    "ko"           : u"Korean",
    "kr"           : u"Kanuri",
    "ks"           : u"Kashmiri",
    "ksh"          : u"Ripuarian",
    "ku"           : u"Kurdish",
    "kv"           : u"Komi",
    "kw"           : u"Cornish",
    "ky"           : u"Kirghiz",
    "la"           : u"Latin",
    "lad"          : u"Ladino",
    "lbe"          : u"Lak",
    "lb"           : u"Luxemburguish",
    "lg"           : u"Ganda",
    "li"           : u"Limburgian",
    "lij"          : u"Ligurian",
    "lld"          : u"Ladin",
    "lmo"          : u"Lombard",
    "ln"           : u"Lingala",
    "lo"           : u"Laotian",
    "lt"           : u"Lithuanian",
    "lv"           : u"Latvian",
    "lzz"          : u"Laz",
    "map-bms"      : u"Banyumasan",
    "mg"           : u"Malagasy",
    "mh"           : u"Marshallese",
    "mi"           : u"Maori",
    "minnan"       : u"Min-nan",
    "mk"           : u"Macedonian",
    "ml"           : u"Malayalam",
    "mn"           : u"Mongoloian",
    "mo"           : u"Moldovan",
    "mr"           : u"Marathi",
    "ms"           : u"Malay",
    "mt"           : u"Maltese",
    "mus"          : u"Creek",
    "my"           : u"Burmese",
    "mzn"          : u"Mazandarin",
    "na"           : u"Nauruan",
    "nah"          : u"Nahuatl",
    "nan"          : u"Min-nan",
    "nap"          : u"Neapolitan",
    "nb"           : u"Norwegian (Bokmal)",
    "nds"          : u"Low German",
    "nds-nl"       : u"Dutch Low Saxon",
    "ne"           : u"Nepali",
    "new"          : u"Newar/Nepal Bhasa",
    "ng"           : u"Ndonga",
    "nl"           : u"Dutch",
    "nn"           : u"Norwegian (Nynorsk)",
    "no"           : u"Norwegian",
    "non"          : u"Old Norse",
    "nov"          : u"Novial",
    "nrm"          : u"Norman",
    "nv"           : u"Navajo",
    "ny"           : u"Chichewa",
    "oc"           : u"Occitan",
    "om"           : u"Oromo",
    "or"           : u"Oriya",
    "os"           : u"Ossetic",
    "pa"           : u"Punjabi",
    "pag"          : u"Pangasinan",
    "pam"          : u"Pampanga",
    "pap"          : u"Papiamentu",
    "pdc"          : u"Pennsylvania German",
    "pih"          : u"Norfuk/Pitcairn/Norfolk",
    "pi"           : u"Pali",
    "pl"           : u"Polish",
    "pms"          : u"Piedmontese",
    "ps"           : u"Pashto",
    "pt"           : u"Portuguese",
    "pt-br"        : u"Brazilian Portuguese",
    "qu"           : u"Quechua",
    "rm"           : u"Raeto-Romance",
    "rmy"          : u"Vlax Romany",
    "rn"           : u"Kirundi",
    "ro"           : u"Romanian",
    "roa-rup"      : u"Aromanian",
    "roa-tara"     : u"Tarantino",
    "ru"           : u"Russian",
    "ru-sib"       : u"Siberian/North Russian",
    "rw"           : u"Kinyarwanda",
    "sa"           : u"Sanskrit",
    "sc"           : u"Sardinian",
    "scn"          : u"Sicilian",
    "sco"          : u"Scots",
    "sd"           : u"Sindhi",
    "se"           : u"Northern Sami",
    "sg"           : u"Sango",
    "sh"           : u"Serbocroatian",
    "si"           : u"Sinhalese",
    "simple"       : u"Simple English",
    "sk"           : u"Slovak",
    "sl"           : u"Slovenian",
    "sm"           : u"Samoan",
    "sn"           : u"Shona",
    "so"           : u"Somali",
    "sq"           : u"Albanian",
    "sr"           : u"Serbian",
    "sr-ec"        : u"Serbian cyrillic ekavian",
    "sr-jc"        : u"Serbian cyrillic iyekvian",
    "sr-el"        : u"Serbian latin ekavian",
    "sr-jl"        : u"Serbian latin iyekavian",
    "ss"           : u"Swati",
    "st"           : u"Southern Sotho",
    "su"           : u"Sundanese",
    "sv"           : u"Swedish",
    "sw"           : u"Swahili",
    "ta"           : u"Tamil",
    "te"           : u"Telugu",
    "tet"          : u"Tetun",
    "tg"           : u"Tajik",
    "th"           : u"Thai",
    "ti"           : u"Tigrinya",
    "tk"           : u"Turkmen",
    "tl"           : u"Tagalog (Filipino)",
    "tlh"          : u"Klingon",
    "tn"           : u"Setswana",
    "to"           : u"Tonga (Tonga Islands)",
    "tokipona"     : u"Toki Pona",
    "tp"           : u"Toki Pona",
    "tpi"          : u"Tok Pisin",
    "tr"           : u"Turkish",
    "ts"           : u"Tsonga",
    "tt"           : u"Tatar",
    "tum"          : u"Tumbuka",
    "tw"           : u"Twi",
    "ty"           : u"Tahitian",
    "tyv"          : u"Tyvan",
    "udm"          : u"Udmurt",
    "ug"           : u"Uyghur",
    "uk"           : u"Ukrainian",
    "ur"           : u"Urdu",
    "uz"           : u"Uzbek",
    "ve"           : u"Venda",
    "vec"          : u"Venetian",
    "vi"           : u"Vietnamese",
    "vls"          : u"West Flemish",
    "vo"           : u"Volapuk",
    "wa"           : u"Walloon",
    "war"          : u"Waray-Waray",
    "wo"           : u"Wolof",
    "wuu"          : u"Wu",
    "xal"          : u"Kalmyk",
    "xh"           : u"Xhosan",
    "yi"           : u"Yiddish",
    "yo"           : u"Yoruba",
    "za"           : u"Zhuang",
    "zea"          : u"Zealandic",
    "zh"           : u"Chinese", # correct?
    "zh-cfr"       : u"Min-nan",
    "zh-classical" : u"Classical Chinese/Literary Chinese",
    "zh-cn"        : u"Simplified",
    "zh-hk"        : u"Traditional (Hong Kong)",
    "zh-min-nan"   : u"Min-nan",
    "zh-sg"        : u"Simplified (Singapore)",
    "zh-tw"        : u"Traditional",
    "zh-yue"       : u"Cantonese",
    "zu"           : u"Zulu",
}

### WIKIPEDIALINK ####################################################################################
# Currently not in use.

class WikipediaLink:
    
    def __init__(self, page, anchor=u"", display=u""):
        
        self.page = page
        self.anchor = anchor
        self.display = display
        
    def __str__(self):
        return self.page.encode("utf-8")
    
    def __unicode__(self):
        return self.page
        
### WIKIPEDIAPARAGRAPH ###############################################################################

class WikipediaParagraph(list):
    
    def __init__(self, title=u"", main=[], related=[], tables=[]):
        
        self.title = title
        self.main = main
        self.related = related
        self.tables = []
        
        self.depth = 0
        self.parent = None
        self.children = []
        
    def __str__(self):
        s = "\n\n".join(self)
        return s.encode("utf-8")

    def __unicode__(self):
        s = "\n\n".join(self)
        return s
 
### WIKIPEDIAIMAGE ###################################################################################
    
class WikipediaImage:
    
    def __init__(self, path, description=u"", links=[], properties=[]):
        
        self.path = path
        self.description = description
        self.links = links
        self.properties = properties
        
    def __str__(self):
        return self.path.encode("utf-8")

    def __unicode__(self):
        return self.path

### WIKIPEDIAREFERENCES ##############################################################################

class WikipediaReference:
    
    def __init__(self, title=u"", url=u""):
        
        self.title = title
        self.url = url
        self.author    = u""
        self.first     = u""
        self.last      = u""
        self.journal   = u""
        self.publisher = u""
        self.date      = u""
        self.year      = u""
        self.id        = u""
        
        self.note      = u""
        
    def __str__(self):
        
        s = ""
        for key in ["note", "author", "title", "journal", "publisher", "date", "id", "url"]:
            value = getattr(self, key)
            if value != "":
                s += value.rstrip(".,") + ", "
        
        s = s.strip(", \n")
        return s.encode("utf-8")
        
    def __unicode__(self):
        return str(self).decode("utf-8")

### WIKIPEDIATABLE ###################################################################################

class WikipediaTable(list):
    
    def __init__(self, title=u"", properties=u"", paragraph=None):
        
        self.title = u""
        self.properties = properties
        self.paragraph = None
      
class WikipediaTableRow(list):
    
    def __init__(self, heading=False, properties=u""):
        
        self.properties = properties

class WikipediaTableCell(unicode):
    
    def __init__(self, data):
        
        unicode.__init__(self, data)
        self.properties = u""

### WIKIPEDIAPAGE ####################################################################################

class WikipediaPage:
    
    def __init__(self, title, markup, light=False, full_strip=True):
        
        """ Wikipedia page parser.
        
        The expected markup is the stuff in Wikipedia's edit textarea.
        With light=True, it will onlt parse links to other articles (which is faster).
        With full_strip=False, it will preserve some HTML markup (links, bold, italic).
        
        """
        
        self.title = title
        self.markup = markup
        self.full_strip = full_strip
        
        self.disambiguation = []
        self.categories = []
        self.links = []
        
        self.paragraphs = []
        self.images = []
        self.tables = []
        self.references = []
        self.translations = {}
        self.important = []
        
        # Main regular expressions used in the parser.
        self.re = {
            "disambiguation" : r"\{\{dablink\|(.*)\}\}",
            "category"       : r"\[\[[:]{0,1}Category:(.*?)\]\]",
            "link"           : r"\[\[([^\:]*?)\]\]",
            "image"          : re.compile(r"\[\[Image:[^\[]*\|.*\]\]", re.I),
            "gallery"        : re.compile("<gallery>(.*?)</gallery>", re.DOTALL),
            "table"          : re.compile(r"\{\|.*?\|\}", re.DOTALL),
            "html-table"     : re.compile(r"<table.*?>.*?</table>", re.DOTALL),
            "reference"      : re.compile(r"<ref.*?>.*?</ref>", re.DOTALL),
            "citation"       : re.compile(r"\{\{cite.*?\}\}", re.DOTALL),
            "url"            : r"\[(http\://.*?)\]",            
            "preformatted"   : re.compile(r"<pre.*?>.*?</pre>", re.DOTALL),
            "translation"    : r"\[\[([^\].]*?):(.*?)\]\]",
            "bold"           : r"\'\'\'(.*?)\'\'\'",
            "comment"        : re.compile(r"<!--.*?-->", re.DOTALL),       
        }
        
        # In the process of stripping references and citations from the markup,
        # they are temporarily marked by this pattern.
        # Don't use any regex characters in it.
        self.ref = "--REF--"
        
        self.parse(light)

    def __unicode__(self):
        
        str = u""
        for paragraph in self.paragraphs:
            str += paragraph.title+"\n\n"
            for textblock in paragraph:
                str += unicode(textblock)+"\n\n"
        
        return str
        
    def __str__(self):
        s = ""
        for p in self.paragraphs:
            s += (p.title.encode("utf-8") + "\n\n").lstrip("\n")
            s += (str(p) + "\n\n").lstrip("\n")
        return s
    
    def __unicode__(self):
        return str(self).decode("utf-8")

    def parse(self, light=False):

        """ Parses data from Wikipedia page markup.

        The markup comes from Wikipedia's edit page.
        We parse it here into objects containing plain text.
        The light version parses only links to other articles, it's faster than a full parse.    
        
        """

        markup = self.markup
        
        self.disambiguation = self.parse_disambiguation(markup)
        self.categories = self.parse_categories(markup)
        self.links = self.parse_links(markup)
        
        if not light:
        
            # Conversion of HTML markup to Wikipedia markup.
            markup = self.convert_pre(markup)
            markup = self.convert_li(markup)
            markup = self.convert_table(markup)
            markup = replace_entities(markup)
        
            # Harvest references from the markup
            # and replace them by footnotes.
            markup = markup.replace("{{Cite", "{{cite")
            markup = re.sub("\{\{ {1,2}cite", "{{cite", markup)
            self.references, markup = self.parse_references(markup)

            # Make sure there are no legend linebreaks in image links.
            # Then harvest images and strip them from the markup.
            markup = re.sub("\n+(\{\{legend)", "\\1", markup)
            self.images, markup = self.parse_images(markup)
            self.images.extend(self.parse_gallery_images(markup))
            
            self.paragraphs = self.parse_paragraphs(markup)
            self.tables = self.parse_tables(markup)
            self.translations = self.parse_translations(markup)
            self.important = self.parse_important(markup)
    
    def plain(self, markup):
        
        """ Strips Wikipedia markup from given text.
        
        This creates a "plain" version of the markup,
        stripping images and references and the like.
        Does some commonsense maintenance as well,
        like collapsing multiple spaces.
        If you specified full_strip=False for WikipediaPage instance,
        some markup is preserved as HTML (links, bold, italic).
        
        """
        
        # Strip bold and italic.
        if self.full_strip:
            markup = markup.replace("'''", "")
            markup = markup.replace("''", "")
        else:
            markup = re.sub("'''([^']*?)'''", "<b>\\1</b>", markup)
            markup = re.sub("''([^']*?)''", "<i>\\1</i>", markup)
        
        # Strip image gallery sections.
        markup = re.sub(self.re["gallery"], "", markup)
        
        # Strip tables.
        markup = re.sub(self.re["table"], "", markup)
        markup = markup.replace("||", "")
        markup = markup.replace("|}", "")
        
        # Strip links, keeping the display alias.
        # We'll strip the ending ]] later.
        if self.full_strip:
            markup = re.sub(r"\[\[[^\]]*?\|", "", markup)
        else:
            markup = re.sub(r"\[\[([^]|]*|)\]\]", '<a href="\\1">\\1</a>', markup)
            markup = re.sub(r"\[\[([^]|]*|)\|([^]]*)\]\]", '<a href="\\1">\\2</a>', markup)    

        # Strip translations, users, etc.
        markup = re.sub(self.re["translation"], "", markup)
        
        # This math TeX is not supported:
        markup = markup.replace("\displaytyle", "")
        markup = markup.replace("\textstyle", "")
        markup = markup.replace("\scriptstyle", "")
        markup = markup.replace("\scriptscriptstyle", "")
        
        # Before stripping [ and ] brackets,
        # make sure they are retained inside <math></math> equations.
        markup = re.sub("(<math>.*?)\[(.*?</math>)", "\\1MATH___OPEN\\2", markup)
        markup = re.sub("(<math>.*?)\](.*?</math>)", "\\1MATH___CLOSE\\2", markup)
        markup = markup.replace("[", "")
        markup = markup.replace("]", "")
        markup = markup.replace("MATH___OPEN", "[")
        markup = markup.replace("MATH___CLOSE", "]")
        
        # a) Strip references.
        # b) Strip <ref></ref> tags.
        # c) Strip <ref name="" /> tags.
        # d) Replace --REF--(12) by [12].
        # e) Remove space between [12] and trailing punctuation .,
        # f) Remove HTML comment <!-- -->
        # g) Keep the Latin Extended-B template: {{latinx| }}
        # h) Strip Middle-Earth references.
        # i) Keep quotes: {{quote| }}
        # j) Remove templates
        markup = re.sub(self.re["reference"], "", markup)                  # a
        markup = re.sub("</{0,1}ref.*?>", "", markup)                      # b
        markup = re.sub("<ref name=\".*?\" {0,1}/>", "", markup)           # c
        markup = re.sub(self.ref+"\(([0-9]*?)\)", "[\\1] ", markup)        # d
        markup = re.sub("\] ([,.\"\?\)])", "]\\1", markup)                 # e
        markup = re.sub(self.re["comment"], "", markup)                    # f
        markup = re.sub("\{\{latinx\|(.*?)\}\}", "\\1", markup)            # g
        markup = re.sub("\{\{ME-ref.*?\}\}", "", markup)                   # h
        markup = re.sub("\{\{quote\|(.*?)\}\}", "\"\\1\"", markup)         # i
        markup = re.sub(re.compile("\{\{.*?\}\}", re.DOTALL), "", markup)  # j
        markup = markup.replace("}}", "")
        
        # Collapse multiple spaces between words,
        # unless they appear in preformatted text.
        markup = re.sub("<br.*?/{0,1}>", " ", markup)
        markup = markup.split("\n")
        for i in range(len(markup)):
            if not markup[i].startswith(" "):
                markup[i] = re.sub(r"[ ]+", " ", markup[i])
        markup = "\n".join(markup)
        markup = markup.replace(" .", ".")
        
        # Strip all HTML except <math> tags.
        if self.full_strip:
            markup = strip_tags(markup, exclude=["math"], linebreaks=True)
        
        markup = markup.strip()
        return markup
    
    def convert_pre(self, markup):
        
        """ Substitutes <pre> to Wikipedia markup by adding a space at the start of a line.
        """
        
        for m in re.findall(self.re["preformatted"], markup):
            markup = markup.replace(m, m.replace("\n", "\n "))
            markup = re.sub("<pre.*?>\n{0,}", "", markup)
            markup = re.sub("\W{0,}</pre>", "", markup)
        
        return markup
    
    def convert_li(self, markup):

        """ Subtitutes <li> content to Wikipedia markup.
        """
        
        for li in re.findall("<li;*?>", markup):
            markup = re.sub(li, "\n* ", markup)
        markup = markup.replace("</li>", "")
            
        return markup
    
    def convert_table(self, markup):
        
        """ Subtitutes <table> content to Wikipedia markup.
        """
        
        for table in re.findall(self.re["html-table"], markup):
            wiki = table
            wiki = re.sub(r"<table(.*?)>", "{|\\1", wiki)
            wiki = re.sub(r"<tr(.*?)>", "|-\\1", wiki)
            wiki = re.sub(r"<td(.*?)>", "|\\1|", wiki)
            wiki = wiki.replace("</td>", "\n")
            wiki = wiki.replace("</tr>", "\n")
            wiki = wiki.replace("</table>", "\n|}")
            markup = markup.replace(table, wiki)
        
        return markup
    
    def parse_links(self, markup):
        
        """ Returns a list of internal Wikipedia links in the markup.

        # A Wikipedia link looks like:
        # [[List of operating systems#Embedded | List of embedded operating systems]]
        # It does not contain a colon, this indicates images, users, languages, etc.
        
        The return value is a list containing the first part of the link,
        without the anchor.

        """
        
        links = []
        m = re.findall(self.re["link"], markup)
        for link in m:
            # We don't like [[{{{1|Universe (disambiguation)}}}]]
            if link.find("{") >= 0:
                link = re.sub("\{{1,3}[0-9]{0,2}\|", "", link)
                link = link.replace("{", "")
                link = link.replace("}", "")            
            link = link.split("|")
            link[0] = link[0].split("#")
            page = link[0][0].strip()
            #anchor = u""
            #display = u""
            #if len(link[0]) > 1: 
            #    anchor = link[0][1].strip()
            #if len(link) > 1: 
            #    display = link[1].strip()
            if not page in links:
                links.append(page)
                #links[page] = WikipediaLink(page, anchor, display)
        
        links.sort()
        return links

    def parse_images(self, markup, treshold=6):
        
        """ Returns a list of images found in the markup.
        
        An image has a pathname, a description in plain text
        and a list of properties Wikipedia uses to size and place images.

        # A Wikipedia image looks like:
        # [[Image:Columbia Supercomputer - NASA Advanced Supercomputing Facility.jpg|right|thumb|
        #   The [[NASA]] [[Columbia (supercomputer)|Columbia Supercomputer]].]]
        # Parts are separated by "|".
        # The first part is the image file, the last part can be a description.
        # In between are display properties, like "right" or "thumb".
        
        """
        
        images = []
        m = re.findall(self.re["image"], markup)
        for p in m:
            p = self.parse_balanced_image(p)
            img = p.split("|")
            path = img[0].replace("[[Image:", "").strip()
            description = u""
            links = {}
            properties = []
            if len(img) > 1:
                img = "|".join(img[1:])
                links = self.parse_links(img)
                properties = self.plain(img).split("|")
                description = u""
                # Best guess: an image description is normally
                # longer than six characters, properties like
                # "thumb" and "right" are less than six characters.
                if len(properties[-1]) > treshold:
                    description = properties[-1]
                    properties = properties[:-1]
            img = WikipediaImage(path, description, links, properties)
            images.append(img)
            markup = markup.replace(p, "")
        
        return images, markup.strip()
    
    def parse_balanced_image(self, markup):
        
        """ Corrects Wikipedia image markup.

        Images have a description inside their link markup that 
        can contain link markup itself, make sure the outer "[" and "]" brackets 
        delimiting the image are balanced correctly (e.g. no [[ ]] ]]).

        Called from parse_images().

        """

        opened = 0
        closed = 0
        for i in range(len(markup)):
            if markup[i] == "[": opened += 1
            if markup[i] == "]": closed += 1
            if opened == closed:
                return markup[:i+1]
                
        return markup

    def parse_gallery_images(self, markup):
        
        """ Parses images from the <gallery></gallery> section.
        
        Images inside <gallery> tags do not have outer "[[" brackets.
        Add these and then parse again.
        
        """
        
        gallery = re.search(self.re["gallery"], markup)
        if gallery:
            gallery = gallery.group(1)
            gallery = gallery.replace("Image:", "[[Image:")
            gallery = gallery.replace("\n", "]]\n")
            images, markup = self.parse_images(gallery)
            return images
        
        return []
    
    def parse_paragraph(self, markup):
        
        """ Creates a list from lines of text in a paragraph.
        
        Each line of text is a new item in the list,
        except lists and preformatted chunks (<li> and <pre>),
        these are kept together as a single chunk.
        
        Lists are formatted using parse_paragraph_list().
        
        Empty lines are stripped from the output.
        Indentation (i.e. lines starting with ":") is ignored.
        
        Called from parse_paragraphs() method.
        
        """
        
        s = self.plain(markup)
        # Add an extra linebreak between the last list item
        # and the normal line following after it, so they don't stick together, e.g.
        # **[[Alin Magic]], magic used in the videogame ''[[Rise of Nations: Rise of Legends]]''
        # In '''popular culture''':
        # * [[Magic (film)|''Magic'' (film)]], a 1978 film starring Anthony Hopkins and Ann-Margret
        s = re.sub(re.compile("\n([*#;].*?)\n([^*#?])", re.DOTALL), "\n\\1\n\n\\2", s)
        # This keeps list items with linebreaks 
        # between them nicely together.
        s = re.sub("\n{2,3}([*#;])", "\n\\1", s)
        chunks = []
        ch = ""
        i = 1
        for chunk in s.split("\n"):
            if chunk.startswith(":"):
                chunk = chunk.lstrip(":")
            if len(chunk.strip()) > 1:
                # Leave out taxoboxes and infoboxes.
                if not chunk.startswith("|"):
                    ch += chunk + "\n"
            if ch.strip() != "":
                if not re.search("^[ *#;]", chunk):
                    ch = self.parse_paragraph_list(ch)
                    chunks.append(ch.rstrip())
                    ch = ""

        if ch.strip() != "":
            ch = self.parse_paragraph_list(ch)
            chunks.append(ch.strip())
            
        return chunks        
    
    def parse_paragraph_list(self, markup, indent="\t"):
        
        """ Formats bullets and numbering of Wikipedia lists.
        
        List items are marked by "*", "#" or ";" at the start of a line.
        We treat ";" the same as "*",
        and replace "#" with real numbering (e.g. "2.").
        Sublists (e.g. *** and ###) get indented by tabs.
        
        Called from parse_paragraphs() method.
        
        """

        def lastleft(ch, str):
            n = 0
            while n < len(str) and str[n] == ch: n += 1
            return n        

        tally = [1 for i in range(10)]
        chunks = markup.split("\n")
        for i in range(len(chunks)):
            if chunks[i].startswith("#"):
                j = min(lastleft("#", chunks[i]), len(tally)-1)
                chunks[i] = indent*(j-1) + str(tally[j])+". " + chunks[i][j:]
                chunks[i] = chunks[i].replace(".  ", ". ")
                tally[j] += 1
                # Reset the numbering of sublists.
                for k in range(j+1, len(tally)): 
                    tally[k] = 1
            if chunks[i].startswith(";"):
                chunks[i] = "*" + chunks[i][1:]
            if chunks[i].startswith("*"):
                j = lastleft("*", chunks[i])  
                chunks[i] = indent*(j-1) + "* " + chunks[i][j:]
                chunks[i] = chunks[i].replace("*  ", "* ")
        
        return "\n".join(chunks)
    
    def parse_paragraph_heading_depth(self, markup):
        
        """ Returns the depth of a heading.
        
        The depth determines parent and child relations,
        which headings (and hence which paragraphs) are a child to a heading higher up.
        Returns 0 for <h1> =, 1 for <h2> ==, etc.
        
        Called from parse_paragraphs() method.
        
        """
        
        return markup.count("=")/2 - 1
        
    def connect_paragraph(self, paragraph, paragraphs):
        
        """ Create parent/child links to other paragraphs.
        
        The paragraphs parameters is a list of all the paragraphs
        parsed up till now.
        
        The parent is the previous paragraph whose depth is less.
        The parent's children include this paragraph.
        
        Called from parse_paragraphs() method.
        
        """

        if paragraph.depth > 0:
            n = range(len(paragraphs))
            n.reverse()
            for i in n:
                if paragraphs[i].depth == paragraph.depth-1:
                    paragraph.parent = paragraphs[i]
                    paragraphs[i].children.append(paragraph)
                    break
                    
        return paragraph          

    def parse_paragraph_references(self, markup):
        
        """ Updates references with content from specific paragraphs.
        
        The "references", "notes", "external links" paragraphs 
        are double-checked for references. Not all items in the list
        might have been referenced inside the article, or the item
        might contain more info than we initially parsed from it.
        
        Called from parse_paragraphs() method.
        
        """
        
        for chunk in markup.split("\n"):
            # We already parsed this, it contains the self.ref mark.
            # See if we can strip more notes from it.
            m = re.search(self.ref+"\(([0-9]*?)\)", chunk)
            if m:
                chunk = chunk.strip("* ")
                chunk = chunk.replace(m.group(0), "")
                chunk = self.plain(chunk)
                i = int(m.group(1))
                if chunk != "":
                    self.references[i-1].note = chunk
            # If it's not a citation we don't have this reference yet.
            elif chunk.strip().startswith("*") \
             and chunk.find("{{cite") < 0:
                chunk = chunk.strip("* ")
                chunk = self.plain(chunk)
                if chunk != "":
                    r = WikipediaReference()
                    r.note = chunk
                    self.references.append(r)
    
    def parse_paragraphs(self, markup):
        
        """ Returns a list of paragraphs in the markup.
        
        A paragraph has a title and multiple lines of plain text.
        A paragraph might have parent and child paragraphs,
        denoting subtitles or bigger chapters.
        
        A paragraph might have links to additional articles.
        
        Formats numbered lists by replacing # by 1.
        Formats bulleted sublists like ** or *** with indentation.
        
        """
        
        # Paragraphs to exclude.
        refs = ["references", "notes", "notes and references", "external links", "further reading"]
        exclude = ["see also", "media", "gallery", "related topics", "lists", "gallery", "images"]
        exclude.extend(refs)
        
        paragraphs = []
        paragraph = WikipediaParagraph(self.title)
        paragraph_data = ""
        for chunk in markup.split("\n"):
            
            # Strip each line of whitespace, 
            # unless it's a preformatted line (starts with a space).
            if not chunk.startswith(" "):
                chunk = chunk.strip()
                
            # A title wrapped in "=", "==", "==="...
            # denotes a new paragraphs section.
            if chunk.startswith("="):

                if paragraph.title.lower() in refs \
                or (paragraph.parent and paragraph.parent.title.lower() in refs):
                    self.parse_paragraph_references(paragraph_data)
                paragraph.extend(self.parse_paragraph(paragraph_data))
                paragraphs.append(paragraph)
                
                # Initialise a new paragraph.
                # Create parent/child links to other paragraphs.
                title = chunk.strip().strip("=")
                title = self.plain(title)
                paragraph = WikipediaParagraph(title)
                paragraph.depth = self.parse_paragraph_heading_depth(chunk)
                if paragraph.title.lower() not in exclude:
                    paragraph = self.connect_paragraph(paragraph, paragraphs)
                paragraph_data = ""
            
            # Underneath a title might be links to in-depth articles,
            # e.g. Main articles: Computer program and Computer programming
            # which in wiki markup would be {{main|Computer program|Computer programming}}
            # The second line corrects" {{Main|Credit (finance)}} or {{Main|Usury}}".
            elif re.search(re.compile("^{{main", re.I), chunk):
                paragraph.main = [link.strip("} ") for link in chunk.split("|")[1:]]
                paragraph.main = [re.sub(re.compile("}}.*?{{main", re.I), "", link) 
                                  for link in paragraph.main]
                
            # At the bottom might be links to related articles,
            # e.g. See also: Abundance of the chemical elements
            # which in wiki markup would be {{see also|Abundance of the chemical elements}}
            elif re.search(re.compile("^{{see {0,1}also", re.I), chunk):
                paragraph.related = [link.strip("} ") for link in chunk.split("|")[1:]]
                
            # Accumulate the data in this paragraph,
            # we'll process it once a new paragraph starts.
            else:
                paragraph_data += chunk +"\n"
                
        # Append the last paragraph.
        if paragraph.title.lower() in refs \
        or (paragraph.parent and paragraph.parent.title.lower() in refs):
            self.parse_paragraph_references(paragraph_data)
        paragraph.extend(self.parse_paragraph(paragraph_data))
        paragraphs.append(paragraph)

        # The "See also" paragraph is an enumeration of links
        # which we already parsed so don't show them.
        # We also did references, and other paragraphs are not that relevant.        
        paragraphs_exclude = []
        for paragraph in paragraphs:
            if paragraph.title.lower() not in exclude \
            and not (paragraph.parent and paragraph.parent.title.lower() in exclude):
                paragraphs_exclude.append(paragraph)
        
        if len(paragraphs_exclude) == 1 and \
           len(paragraphs_exclude[0]) == 0:
            return []
        
        return paragraphs_exclude    

    def parse_table_row(self, markup, row):

        """ Parses a row of cells in a Wikipedia table.
        
        Cells in the row are separated by "||".
        A "!" indicates a row of heading columns.
        Each cell can contain properties before a "|",
        # e.g. align="right" | Cell 2 (right aligned).       
        
        """
        
        if row == None:
            row = WikipediaTableRow()
           
        markup = markup.replace("!!", "||")
        for cell in markup.lstrip("|!").split("||"):
            # The "|" after the properties can't be part of a link.
            i = cell.find("|")
            j = cell.find("[[")
            if i>0 and (j<0 or i<j):
                data = self.plain(cell[i+1:])
                properties = cell[:i].strip()
            else:
                data = self.plain(cell)
                properties = u""
            cell = WikipediaTableCell(data)
            cell.properties = properties
            row.append(cell)
        
        return row

    def connect_table(self, table, chunk, markup):

        """ Creates a link from the table to paragraph and vice versa.
        
        Finds the first heading above the table in the markup.
        This is the title of the paragraph the table belongs to.
        
        """

        k = markup.find(chunk)
        i = markup.rfind("\n=", 0, k)
        j = markup.find("\n", i+1)
        paragraph_title = markup[i:j].strip().strip("= ")
        for paragraph in self.paragraphs:
            if paragraph.title == paragraph_title:
                paragraph.tables.append(table)
                table.paragraph = paragraph

    def parse_tables(self, markup):
        
        """ Returns a list of tables in the markup.

        A Wikipedia table looks like:
        {| border="1"
        |-
        |Cell 1 (no modifier - not aligned)
        |-
        |align="right" |Cell 2 (right aligned)
        |-
        |}

        """

        tables = []
        m = re.findall(self.re["table"], markup)
        for chunk in m:

            table = WikipediaTable()
            table.properties = chunk.split("\n")[0].strip("{|").strip()
            self.connect_table(table, chunk, markup)
                  
            # Tables start with "{|".
            # On the same line can be properties, e.g. {| border="1"
            # The table heading starts with "|+".
            # A new row in the table starts with "|-".
            # The end of the table is marked with "|}".            
            row = None
            for chunk in chunk.split("\n"):
                chunk = chunk.strip()
                if chunk.startswith("|+"):
                    title = self.plain(chunk.strip("|+"))
                    table.title = title
                elif chunk.startswith("|-"):
                    if row: 
                        row.properties = chunk.strip("|-").strip()
                        table.append(row)
                    row = None
                elif chunk.startswith("|}"):
                    pass
                elif chunk.startswith("|") \
                  or chunk.startswith("!"):
                    row = self.parse_table_row(chunk, row)
                        
            # Append the last row.
            if row: table.append(row)
            if len(table) > 0:
                tables.append(table)
        
        return tables

    def parse_references(self, markup):

        """ Returns a list of references found in the markup.
        
        References appear inline as <ref> footnotes, 
        http:// external links, or {{cite}} citations.
        We replace it with (1)-style footnotes.
        Additional references data is gathered in
        parse_paragraph_references() when we parse paragraphs.
        
        References can also appear in image descriptions,
        tables and taxoboxes, so they might not always pop up in a paragraph.
        
        The plain() method finally replaces (1) by [1].
        
        """
    
        references = []
        
        # A Wikipedia reference note looks like:
        # <ref>In 1946, [[ENIAC]] consumed an estimated 174 kW. 
        # By comparison, a typical personal computer may use around 400 W; 
        # over four hundred times less. {{Ref harvard|kempf1961|Kempf 1961|a}}</ref>
        m = re.findall(self.re["reference"], markup)
        for reference in m:
            reference = re.sub("<ref> {0,1}cite", "<ref>{{cite", reference)
            if not reference.strip().startswith("[http://") and \
               not re.search("\{\{cite", reference):
                r = WikipediaReference()
                r.note = self.plain(re.sub("</{0,1}ref.*?>", "", reference))
                if r.note != "":
                    references.append(r)
                    p = " "+self.ref+"("+str(len(references))+")"
                    markup = markup.replace(reference, p, 1)
            else:
                # References containing a citation or url 
                # are better handled by the next patterns.
                pass
        
        # A Wikipedia citation looks like:
        # {{cite journal
        # | last = Einstein 
        # | first = Albert
        # | authorlink = Albert Einstein
        # | title = Sidelights on Relativity (Geometry and Experience) 
        # | publisher = P. Dutton., Co 
        # | date = 1923}}
        m = re.findall(self.re["citation"], markup)
        for citation in m:
            c = citation.replace("\n", "")
            r = WikipediaReference()
            for key in r.__dict__.keys():
                value = re.search("\| {0,1}"+key+"(.*?)[\|}]", c)
                if value:
                    value = value.group(1)
                    value = value.replace("link", "")
                    value = value.strip().strip(" =[]")
                    value = self.plain(value)
                    setattr(r, key, value)
            if r.first != "" and r.last != "":
                r.author = r.first + " " + r.last
            references.append(r)
            p = " "+self.ref+"("+str(len(references))+")"
            markup = markup.replace(citation, p, 1)
        
        # A Wikipedia embedded url looks like:
        # [http://www.pbs.org/wnet/hawking/html/home.html ''Stephen Hawking's Universe'']
        m = re.findall(self.re["url"], markup)
        for url in m:
            r = WikipediaReference()
            i = url.find(" ")
            if i > 0:
                r.url = url[:i].strip()
                r.note = self.plain(url[i:])
            else:
                r.url = url.strip()
            references.append(r)
            p = r.note+" "+self.ref+"("+str(len(references))+")"
            markup = markup.replace("["+url+"]", p, 1)

        # Since we parsed all citations first and then all notes and urls,
        # the ordering will not be correct in the markup,
        # e.g. (1) (11) (12) (2) (3).
        sorted = []
        m = re.findall(self.ref+"\(([0-9]*)\)", markup)
        for i in m:
            sorted.append(references[int(i)-1])
            markup = markup.replace(
                self.ref+"("+i+")", 
                self.ref+"**("+str(len(sorted))+")"
                )
        markup = markup.replace(self.ref+"**", self.ref)
        for r in references:
            if r not in sorted:
                sorted.append(r)
        references = sorted

        return references, markup.strip()
                
    def parse_categories(self, markup):
        
        """ Returns a list of categories the page belongs to.

        # A Wikipedia category link looks like:
        # [[Category:Computing]]
        # This indicates the page is included in the given category.
        # If "Category" is preceded by ":" this indicates a link to a category.
        
        """
        
        categories = []
        m = re.findall(self.re["category"], markup)
        for category in m:
            category = category.split("|")
            page = category[0].strip()
            display = u""
            if len(category) > 1: 
                display = category[1].strip()
            #if not categories.has_key(page):
            #    categories[page] = WikipediaLink(page, u"", display)
            if not page in categories:
                categories.append(page)
                
        return categories
    
    def parse_translations(self, markup):
        
        """ Returns a dictionary of translations for the page title.
        
        A Wikipedia language link looks like: [[af:Rekenaar]].
        The parser will also fetch links like "user:" and "media:"
        but these are stripped against the dictionary of
        Wikipedia languages.
        
        You can get a translated page by searching Wikipedia
        with the appropriate language code and supplying
        the translated title as query.
        
        """
        
        global languages
        translations = {}
        m = re.findall(self.re["translation"], markup)
        for language, translation in m:
            if language in languages:
                translations[language] = translation
         
        return translations
    
    def parse_disambiguation(self, markup):
        
        """ Gets the Wikipedia disambiguation page for this article.
        
        A Wikipedia disambiguation link refers to other pages
        with the same title but of smaller significance,
        e.g. {{dablink|For the IEEE magazine see [[Computer (magazine)]].}}
        
        """
        
        m = re.search(self.re["disambiguation"], markup)
        if m:
            return self.parse_links(m.group(1))
        else:
            return []
    
    def parse_important(self, markup):
        
        """ Returns a list of words that appear in bold in the article.
        
        Things like table titles are not added to the list,
        these are probably bold because it makes the layout nice,
        not necessarily because they are important.
        
        """
        
        important = []
        table_titles = [table.title for table in self.tables]
        m = re.findall(self.re["bold"], markup)
        for bold in m:
            bold = self.plain(bold)
            if not bold in table_titles:
                important.append(bold.lower())
        
        return important

### DRAWING UTILITIES ################################################################################
   
def is_preformatted(str):

    """ Determines if an item in a paragraph is preformatted.

    If all of the lines in the markup start with a " "
    this indicates preformatted text.
    Preformatted is usually used for programming code.

    """

    for chunk in str.split("\n"):
        if  not chunk.startswith(" "):
            return False
    
    return True

def is_list(str):
 
    """ Determines if an item in a paragraph is a list.

    If all of the lines in the markup start with a "*" or "1." 
    this indicates a list as parsed by parse_paragraphs().
    It can be drawn with draw_list().
    
    """ 
    
    for chunk in str.split("\n"):
        chunk = chunk.replace("\t", "")
        if  not chunk.lstrip().startswith("*") \
        and not re.search(r"^([0-9]{1,3}\. )", chunk.lstrip()):
            return False
    
    return True
    
def is_math(str):
    
    """ Determines if an item in a paragraph is a LaTeX math equation.
    
    Math equations are wrapped in <math></math> tags.
    They can be drawn as an image using draw_math().
    
    """
    
    str = str.strip()
    if str.startswith("<math>") and str.endswith("</math>"):
        return True
    else:
        return False
        
def draw_math(str, x, y, alpha=1.0):
    
    """ Uses mimetex to generate a GIF-image from the LaTeX equation.
    """
    
    try: from web import _ctx
    except: pass
    
    str = re.sub("</{0,1}math>", "", str.strip())
    img = mimetex.gif(str)
    w, h = _ctx.imagesize(img)
    _ctx.image(img, x, y, alpha=alpha)
    return w, h

def textwidth(str):
    
    """textwidth() reports incorrectly when lineheight() is smaller than 1.0
    """
    
    try: from web import _ctx
    except: pass
    
    l = _ctx.lineheight()
    _ctx.lineheight(1)
    w = _ctx.textwidth(str)
    _ctx.lineheight(l)
    
    return w            

def draw_list(markup, x, y, w, padding=5, callback=None):
    
    """ Draws list markup with indentation in NodeBox.

    Draw list markup at x, y coordinates
    using indented bullets or numbers.
    The callback is a command that takes a str and an int.
    
    """
    
    try: from web import _ctx
    except: pass

    i = 1
    for chunk in markup.split("\n"):
        
        if callback != None: 
            callback(chunk, i)
        
        m = re.search("^([0-9]{1,3}\. )", chunk.lstrip())
        if m:
            indent = re.search("[0-9]", chunk).start()*padding*2
            bullet = m.group(1)
            dx = textwidth("000.")
            chunk = chunk.lstrip(m.group(1)+"\t")
        
        if chunk.lstrip().startswith("*"):
            indent = chunk.find("*")*padding*2
            bullet = u"•"
            dx = textwidth("*")
            chunk = chunk.lstrip("* \t")
        
        _ctx.text(bullet, x+indent, y)
        dx += padding + indent
        _ctx.text(chunk, x+dx, y, width=w-dx)
        y += _ctx.textheight(chunk, width=w-dx)
        y += _ctx.textheight(" ") * 0.25
        i += 1

def draw_table(table, x, y, w, padding=5):
    
    """ This is a very poor algorithm to draw Wikipedia tables in NodeBox.
    """
    
    try: from web import _ctx
    except: pass
    
    f = _ctx.fill()
    _ctx.stroke(f)
    h = _ctx.textheight(" ") + padding*2
    
    row_y = y
    
    if table.title != "":
        _ctx.fill(f)
        _ctx.rect(x, row_y, w, h)
        _ctx.fill(1)
        _ctx.text(table.title, x+padding, row_y+_ctx.fontsize()+ padding)
        row_y += h
    
    # A table of flags marking how long a cell 
    # from a previous row is still spanning in a column.
    rowspans = [1 for i in range(10)]
    previous_cell_w = 0
    
    for row in table:
        
        cell_x = x
        
        # The width of a cell is the total table width 
        # evenly divided by the number of cells.
        # Previous rows' cells still spanning will push cells
        # to the right and decrease their width.
        cell_w  = 1.0 * w
        cell_w -= previous_cell_w * len([n for n in rowspans if n > 1])
        cell_w /= len(row)
        
        # The height of each cell is the highest cell in the row.
        # The height depends on the amount of text in the cell.
        cell_h = 0
        for cell in row:
            this_h = _ctx.textheight(cell, width=cell_w-padding*2) + padding*2
            cell_h = max(cell_h, this_h)
        
        # Traverse each cell in this row.
        i = 0
        for cell in row:
            
            # If a previous row's cell is still spanning,
            # push this cell to the right.
            if rowspans[i] > 1:
                rowspans[i] -= 1
                cell_x += previous_cell_w
                i += 1
                
            # Get the rowspan attribute for this cell.
            m = re.search("rowspan=\"(.*?)\"", cell.properties)
            if m:
                rowspan = int(m.group(1))
                rowspans[i] = rowspan
            else:
                rowspan = 1

            # Padded cell text.            
            # Horizontal line above each cell.
            # Vertical line before each cell.
            _ctx.fill(f)
            _ctx.text(cell, cell_x+padding, row_y+_ctx.fontsize()+padding, cell_w-padding*2)
            _ctx.line(cell_x, row_y, cell_x+cell_w, row_y)
            if cell_x > x:
                _ctx.nofill()
                _ctx.line(cell_x, row_y, cell_x, row_y+cell_h)
                
            cell_x += cell_w
            i += 1
            
        # Move to next row.
        row_y += cell_h
        previous_cell_w = cell_w
        
    # Table's bounding rectangle.
    _ctx.nofill()
    _ctx.rect(x, y, w, row_y-y)

### WIKIPEDIASEARCH ##################################################################################

class WikipediaSearch(WikipediaPage, URLAccumulator):
    
    def _api_request(self, q, language="en"):

        url  = "http://"+language+".wikipedia.org/w/api.php"
        url += "?action=query&redirects&format=xml&prop=revisions&rvprop=content&titles="
        url += quote(q)
        return url
    
    def __init__(self, q, language="en", light=False, wait=10, asynchronous=False, cached=True,
                 case_sensitive=False, full_strip=True):
        
        """ A download manager for Wikipedia pages.
        
        WikipediaSearch is a combination of
        URLAccumulator that handles asynchronous and cached web downloads and
        WikipediaPage that parses XML retrieved from the Wikipedia API.
        
        Retrieves the latest revision.
        Redirects are handled by the Wikipedia server.
        
        """
        
        self._light = light
        self._full_strip = full_strip
        
        if cached: 
            cache = "wikipedia"
        else:
            cache = None
        
        if not case_sensitive:
            q = str(q.lower())
        q = q.replace(" ", "_")
        url = self._api_request(q, language)
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, type=".xml", throttle=2)

    def load(self, data):
        
        dom = minidom.parseString(self.data)
        page = dom.getElementsByTagName("page")[0]
        title = page.getAttribute("title")
        try:
            rev = dom.getElementsByTagName("rev")[0]
            data = rev.childNodes[0].nodeValue.strip()
        except:
            if not self.error:
                self.error = WikipediaPageMissing()
            data = ""

        WikipediaPage.__init__(self,  title, data, light=self._light, full_strip=self._full_strip)

def search(q, language="en", light=False, wait=10, asynchronous=False, cached=True, 
           case_sensitive=False, full_strip=True):
    return WikipediaSearch(q, language, light, wait, asynchronous, cached, case_sensitive, full_strip)

######################################################################################################
# Some interesting things...
# Redirects are now handled by the Wikipedia server but for some reason I'm keeping this code around.
# The superscript could be used to format references and footnotes.

def is_redirect(page):
    m = re.search(r"#REDIRECT \[\[.*?\]\]", page)
    if m and len(m.group(0)) == len(page):
        return True
    else:
        return False

def redirect(page):
    m = re.search(r"#REDIRECT \[\[(.*?)\]\]", page)
    if m:
        return m.group(1)
    else:
        return None

def superscript(number):
    
    digits = [
        u"\u2070",
        u"\u2071",
        u"\u2072",
        u"\u2073",
        u"\u2074",
        u"\u2075",
        u"\u2076",
        u"\u2077",
        u"\u2078",
        u"\u2079",  
    ]
    
    s = u""
    for digit in str(number):
        s += digits[int(digit)]
        
    return s

######################################################################################################

