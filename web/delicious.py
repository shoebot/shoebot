import urllib2, libxml2, xml.utils.iso8601, md5, re, RDF, datetime, urllib
from sets import Set

def get_url_contents(url):
    try:
        import httpcache
        return httpcache.HTTPCache(url).content()
    except ImportError:
        return urllib.urlopen(url).read()

def _set_auth(username,password):
    authinfo = urllib2.HTTPBasicAuthHandler()
    authinfo.add_password('del.icio.us API', 'http://del.icio.us', username, password)
    opener = urllib2.build_opener(authinfo)
    urllib2.install_opener(opener)

def my_tags(username,password):
    _set_auth(username,password)

    result = Set([])

    xml = libxml2.parseDoc(get_url_contents('http://del.icio.us/api/tags/get'))
    tags = xml.xpathEval("/tags/tag")
    for tag in tags:
        result.add(Tag(tag.prop("tag")))
    return result

def add_post(username,password,url=None,description="",extended="",tags="",dt=None):
    _set_auth(username,password)

    if dt is None:
        dt = datetime.datetime.now()
    if type(dt) is int:
        dt = datetime.datetime.fromtimestamp(dt)
    if isinstance(dt,datetime.date):
        date = dt.strftime("%Y-%m-%dT%H:%m:%SZ")
    else:
        date = str(dt)

    if type(tags) is list:
        tags = " ".join([str(tag) for tag in tags])

    data = {
      'url' : url,
      'description' : description,
      'extended' : extended,
      'tags' : tags,
      'dt' : date,
      }

    posturl = "http://del.icio.us/api/posts/add?"+urllib.urlencode(data)
    urllib2.urlopen(posturl).read()

def my_posts(username,password):
    _set_auth(username,password)

    result = []

    xml = libxml2.parseDoc(get_url_contents('http://del.icio.us/api/posts/recent'))
    posts = xml.xpathEval("/posts/post")
    for post in posts:
        result.append(Post(username,post))
    return result

def posts():
    url = "http://del.icio.us/rss/"

    model = RDF.Model()
    parser = RDF.Parser()
    parser.parse_string_into_model(model,get_url_contents(url),RDF.Uri("http://foo"))
    posts = [RSSTagPost(model,p.subject) for p in model.find_statements(RDF.Statement(None,RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),RDF.Uri("http://purl.org/rss/1.0/item")))]
    return posts

class TagFactory(object):
    def __init__(self):
        pass
    def __getattr__(self,name):
        return Tag(name)

class UserFactory(object):
    def __init__(self):
        pass
    def __getattr__(self,name):
        return User(name)

tags = TagFactory()
users = UserFactory()

class Post(object):
    def __init__(self,user,post_elt):
        self.description = post_elt.prop('description')
        self.time = xml.utils.iso8601.parse(post_elt.prop('time'))
        self.href = Href(post_elt.prop('href'))
        self.tags = Set([Tag(n) for n in post_elt.prop('tag').split(" ")])
        self.extended = post_elt.prop('extended')
        self.user = user

    def __repr__(self):
        return ", ".join([thing+": "+str(self.__dict__[thing]) for thing in self.__dict__])

class User(object):
    def __init__(self,user):
        self.user = user

    def url(self):
        return "http://del.icio.us/"+self.user

    def __iter__(self):
        return PostIterator(self.posts())

    def __call__(self,*args):
        return self.posts(*args)

    def __eq__(self,other):
        return type(self) == type(other) and str(self) == str(other)

    def __hash__(self):
        return self.user.__hash__()

    def __repr__(self):
        return self.user

    def posts(self,*args):
        alltags = Set()
        for arg in args:
            if isinstance(arg,Tag):
                alltags.add(arg)

        url = "http://del.icio.us/rss/"+self.user
        if len(alltags)>0:
            url += "/"+"+".join([str(tag) for tag in alltags])

        model = RDF.Model()
        parser = RDF.Parser()
        try:
            parser.parse_string_into_model(model,get_url_contents(url),RDF.Uri("http://foo"))
            posts = [RSSTagPost(model,p.subject) for p in model.find_statements(RDF.Statement(None,RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),RDF.Uri("http://purl.org/rss/1.0/item")))]
            for post in posts:
                post.user = self
            return posts
        except:
            return []

class Href(object):
    def __init__(self,href):
        self.href = href
        self.hash = md5.md5(self.href).hexdigest()

    def __iter__(self):
        return PostIterator(self.posts())

    def __eq__(self,other):
        return type(self) == type(other) and str(self) == str(other)

    def __hash__(self):
        return self.hash.__hash__()

    def __repr__(self):
        return self.href

    def url(self):
        return "http://del.icio.us/url/"+self.hash

    def posts(self):
        url = "http://del.icio.us/url/"+self.hash
        doc = libxml2.htmlParseDoc(get_url_contents(url),"ISO-8859-1")
        posts = [HtmlPost(p) for p in doc.xpathEval("//div[@class='delPost']")]
        return posts

class HtmlPost(Post):
    def __init__(self,div_elt):
        self.tags = Set([])

        # Note the page being parsed is a non-authenticated version,
        # meaning the delPost divs have no 'copy/edit this item' links

        # href and description
        [delLink] = div_elt.xpathEval("div/a[@class='delLink']")
        self.href = delLink.prop('href')
        self.description = delLink.content

        # extended (if any)
        for div in div_elt.xpathEval("div[count(a)=0]"):
          self.extended = div.content

        # delNav class anchors: first the tags (if any), then user, then date
        delNav = div_elt.xpathEval("div/a[@class='delNav']")
        self.user = delNav[-2].content
        for a in delNav[0:-2]:
          tag = a.lastChild().content
          self.tags.add(Tag(tag))

class PostIterator(object):
    def __init__(self,posts):
        self.posts = posts
        self.idx = 0

    def __iter__(self):
        return self

    def next(self):
        if self.idx<len(self.posts):
            self.idx += 1
            return self.posts[self.idx-1]
        raise StopIteration

class Tag(object):
    def __init__(self,name):
        self.name = name.lower()

    def url(self):
        return "http://del.icio.us/tag/"+self.name

    def __call__(self,*args):
        return self.posts(*args)

    def __eq__(self,other):
        return type(self) == type(other) and str(self) == str(other)

    def __hash__(self):
        return self.name.__hash__()

    def __repr__(self):
        return self.name

    def __iter__(self):
        return PostIterator(self.posts())

    def posts(self,*args):
        alltags = Set()
        extratags = ""
        user = None

        for arg in args:
            if isinstance(arg,Tag):
                alltags.add(arg)
            if isinstance(arg,User):
                user = arg

        if len(alltags)>0:
            extratags = "+"+"+".join([str(tag) for tag in alltags])

        if user is not None:
            url = "http://del.icio.us/rss/"+str(user)+"/"+self.name+extratags
        else:
            url = "http://del.icio.us/rss/tag/"+self.name


        model = RDF.Model()
        parser = RDF.Parser()
        try:
            parser.parse_string_into_model(model,get_url_contents(url),RDF.Uri("http://foo"))
            posts = [RSSTagPost(model,p.subject,self) for p in model.find_statements(RDF.Statement(None,RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),RDF.Uri("http://purl.org/rss/1.0/item")))]
            if user is not None:
                for post in posts:
                    post.user = user
            return posts
        except:
            return []

class RSSTagPost(Post):
    def __init__(self,model,item,tag=None):
        rss = RDF.NS("http://purl.org/rss/1.0/")
        dc = RDF.NS("http://purl.org/dc/elements/1.1/")
        self.description = str(model.get_target(item,rss.title))
        self.extended = str(model.get_target(item,rss.description))
        self.user = User(str(model.get_target(item,dc.creator)))
        dcdate = model.get_target(item,dc.date)
        if dcdate is not None:
            self.time = xml.utils.iso8601.parse(str(dcdate))
        self.href = Href(str(item.uri))
        subject = str(model.get_target(item,dc.subject))
        self.tags = Set([])
        if subject is not None:
            self.tags = Set([Tag(x) for x in subject.split(" ")])
        if tag is not None:
            self.tags.add(tag)

if __name__ == '__main__':
    import sys
    from sets import Set

    username = sys.argv[1]
    user = User(username)
    tags = Set()
    users = {}

    print "Reading "+username+" posts..."
    for post in user:
        for tag in post.tags:
            tags.add(tag)

        other_tags = Set()
        count = 0
        for other_post in post.href:
            u = other_post.user
            if not u == user:
                count += 1
                if u not in users:
                    users[u] = []
                users[u].append(other_post)

                for tag in other_post.tags:
                    if tag not in post.tags:
                        other_tags.add(str(tag))

        if count>0:
            print post.description+" ("+str(post.href)+")..."
            print "  "+username+" tagged thus: "+",".join([str(t) for t in post.tags])
            if len(other_tags)>0:
                print "  "+str(count)+" others tagged further: "+",".join(other_tags)
            else:
                print "  "+str(count)+" others had no further tags to add"
            print

    print "users who posted the same stuff"
    print "-------------------------------"
    print

    for founduser in users:
        if founduser == username: continue
        if len(users[founduser])>2:
            print founduser.url(),"also posted:"
            for post in users[founduser]:
                print " ",post.description
                print "    ("+str(post.href)+")",
                if len(post.tags)>0:
                    print "- "+",".join([str(tag) for tag in post.tags])
                else:
                    print
            print
