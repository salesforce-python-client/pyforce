
from xml.sax import make_parser
from xml.sax.handler import (
    EntityResolver, DTDHandler, ContentHandler,
    ErrorHandler, feature_namespaces
)

__version__ = "2.18"
__author__ = "Aaron Swartz"
__credits__ = "Many thanks to pjz, bitsko, and DanC."
__copyright__ = "(C) 2003-2006 Aaron Swartz. GNU GPL 2."


def isstr(mystring):
    '''Check if string is a string or unicode'''
    return isinstance(mystring, str)


def islst(myitem):
    '''Check if item is a tuple or list'''
    return isinstance(myitem, tuple) or isinstance(myitem, list)

EMPTY = {
    'http://www.w3.org/1999/xhtml': [
        'img', 'br', 'hr', 'meta', 'link', 'base', 'param', 'input', 'col',
        'area'
    ]
}


def quote(myitem, elt=True):
    '''URL encode string'''
    if elt and '<' in myitem and len(myitem) > 24 and myitem.find(']]>') == -1:
        return '<![CDATA[%s]]>' % (myitem)
    else:
        myitem = myitem.replace('&', '&amp;').\
            replace('<', '&lt;').replace(']]>', ']]&gt;')
    if not elt:
        myitem = myitem.replace('"', '&quot;')
    return myitem


class Element(object):
    def __init__(self, name, attrs=None, children=None, prefixes=None):
        if islst(name) and name[0] is None:
            name = name[1]
        if attrs:
            na = {}
            for k in attrs.keys():
                if islst(k) and k[0] is None:
                    na[k[1]] = attrs[k]
                else:
                    na[k] = attrs[k]
            attrs = na

        self._name = name
        self._attrs = attrs or {}
        self._dir = children or []

        prefixes = prefixes or {}
        self._prefixes = dict(zip(prefixes.values(), prefixes.keys()))

        if prefixes:
            self._dNS = prefixes.get(None, None)
        else:
            self._dNS = None

    def __repr__(self, recursive=0, multiline=0, inprefixes=None):
        def qname(name, inprefixes):
            if islst(name):
                if inprefixes[name[0]] is not None:
                    return inprefixes[name[0]]+':'+name[1]
                else:
                    return name[1]
            else:
                return name

        def arep(a, inprefixes, addns=1):
            out = ''

            for p in sorted(self._prefixes.keys()):
                if not p in inprefixes.keys():
                    if addns:
                        out += ' xmlns'
                    if addns and self._prefixes[p]:
                        out += ':'+self._prefixes[p]
                    if addns:
                        out += '="'+quote(p, False)+'"'
                    inprefixes[p] = self._prefixes[p]

            for k in sorted(a.keys()):
                out += ' %s="%s"' % (qname(k, inprefixes), quote(a[k], False))
            return out

        inprefixes = inprefixes or {
            u'http://www.w3.org/XML/1998/namespace': 'xml'
        }

        # need to call first to set inprefixes:
        attributes = arep(self._attrs, inprefixes, recursive)
        out = '<' + qname(self._name, inprefixes) + attributes

        if not self._dir and (self._name[0] in EMPTY.keys()
                              and self._name[1] in EMPTY[self._name[0]]):
            out += ' />'
            return out

        out += '>'

        if recursive:
            content = 0
            for x in self._dir:
                if isinstance(x, Element):
                    content = 1

            pad = '\n' + ('\t' * recursive)
            for x in self._dir:
                if multiline and content:
                    out += pad
                if isstr(x):
                    out += quote(x)
                elif isinstance(x, Element):
                    out += x.__repr__(
                        recursive+1,
                        multiline,
                        inprefixes.copy()
                    )
                else:
                    raise TypeError("I wasn't expecting " + repr(x) + ".")
            if multiline and content:
                out += '\n' + ('\t' * (recursive-1))
        else:
            if self._dir:
                out += '...'

        out += '</'+qname(self._name, inprefixes)+'>'

        return out

    def __unicode__(self):
        text = ''
        for x in self._dir:
            text += x
        return ' '.join(text.split())

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __getattr__(self, n):
        if n[0] == '_':
            raise AttributeError(
                "Use foo['" + n + "'] to access the child element."
            )
        if self._dNS:
            n = (self._dNS, n)
        for x in self._dir:
            if isinstance(x, Element) and x._name == n:
                return x
        raise AttributeError('No child element named %s' % repr(n))

    def __hasattr__(self, n):
        for x in self._dir:
            if isinstance(x, Element) and x._name == n:
                return True
        return False

    def __setattr__(self, n, v):
        if n[0] == '_':
            self.__dict__[n] = v
        else:
            self[n] = v

    def __getitem__(self, n):
        if isinstance(n, int):  # d[1] == d._dir[1]
            return self._dir[n]
        elif isinstance(n, slice) and (
            isinstance(n.start, int) or n.start is None
        ):
            return self._dir[n]
        elif isinstance(n, tuple) and len(n) == 1:  # d['foo',] == all <foo>s
            n = n[0]
            if self._dNS and not islst(n):
                n = (self._dNS, n)
            out = []
            for x in self._dir:
                if isinstance(x, Element) and x._name == n:
                    out.append(x)
            return out
        elif n is None:
            return self._dir
        else:  # d['foo'] == first <foo>
            if self._dNS and not islst(n):
                n = (self._dNS, n)
            for x in self._dir:
                if isinstance(x, Element) and x._name == n:
                    return x
        raise KeyError(n)

    def __setitem__(self, n, v):
        if isinstance(n, type(0)):  # d[1]
            self._dir[n] = v
        elif isinstance(n, tuple) and len(n) == 1:
            # d['foo',] adds a new foo
            n = n[0]
            if self._dNS and not islst(n):
                n = (self._dNS, n)

            nv = Element(n)
            self._dir.append(nv)

        else:  # d["foo"] replaces first <foo> and dels rest
            if self._dNS and not islst(n):
                n = (self._dNS, n)

            nv = Element(n)
            nv._dir.append(v)
            replaced = False

            todel = []
            for i in range(len(self)):
                if self[i]._name == n:
                    if replaced:
                        todel.append(i)
                    else:
                        self[i] = nv
                        replaced = True
            if not replaced:
                self._dir.append(nv)
            for i in todel:
                del self[i]

    def __delitem__(self, n):
        if isinstance(n, type(0)):
            del self._dir[n]
        elif isinstance(n, slice(0).__class__):
            # delete all <foo>s
            n = n.start
            if self._dNS and not islst(n):
                n = (self._dNS, n)

            for i in range(len(self)):
                if self[i]._name == n:
                    del self[i]
        else:
            # delete first foo
            for i in range(len(self)):
                if self[i]._name == n:
                    del self[i]
                break

    def __call__(self, *_pos, **_set):
        if _set:
            for k in _set.keys():
                self._attrs[k] = _set[k]
        if len(_pos) > 1:
            for i in range(0, len(_pos), 2):
                self._attrs[_pos[i]] = _pos[i+1]
        if len(_pos) == 1:
            return self._attrs[_pos[0]]
        if len(_pos) == 0:
            return self._attrs

    def __len__(self):
        return len(self._dir)


class Namespace(object):
    def __init__(self, uri):
        self.__uri = uri

    def __getattr__(self, n):
        return (self.__uri, n)

    def __getitem__(self, n):
        return (self.__uri, n)


class Seeder(EntityResolver, DTDHandler, ContentHandler, ErrorHandler):
    def __init__(self):
        self.stack = []
        self.ch = ''
        self.prefixes = {}
        ContentHandler.__init__(self)

    def startPrefixMapping(self, prefix, uri):
        if not prefix in self.prefixes.keys():
            self.prefixes[prefix] = []
        self.prefixes[prefix].append(uri)

    def endPrefixMapping(self, prefix):
        self.prefixes[prefix].pop()
        # szf: 5/15/5
        if len(self.prefixes[prefix]) == 0:
            del self.prefixes[prefix]

    def startElementNS(self, name, qname, attrs):
        ch = self.ch
        self.ch = ''
        if ch and not ch.isspace():
            self.stack[-1]._dir.append(ch)

        attrs = dict(attrs)
        newprefixes = {}
        for k in self.prefixes.keys():
            newprefixes[k] = self.prefixes[k][-1]

        self.stack.append(Element(name, attrs, prefixes=newprefixes.copy()))

    def characters(self, ch):
        self.ch += ch

    def endElementNS(self, name, qname):
        ch = self.ch
        self.ch = ''
        if ch and not ch.isspace():
            self.stack[-1]._dir.append(ch)

        element = self.stack.pop()
        if self.stack:
            self.stack[-1]._dir.append(element)
        else:
            self.result = element


def seed(fileobj):
    seeder = Seeder()
    parser = make_parser()
    parser.setFeature(feature_namespaces, 1)
    parser.setContentHandler(seeder)
    parser.parse(fileobj)
    return seeder.result


def parse(text):
    from io import StringIO
    return seed(StringIO(text))


def load(url):
    import urllib
    return seed(urllib.urlopen(url))
