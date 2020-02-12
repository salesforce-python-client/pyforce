from pyforce.xmltramp import *

def main_test():
    parse('<doc>a<baz>f<b>o</b>ob<b>a</b>r</baz>a</doc>').__repr__(1, 1) == \
        '<doc>\n\ta<baz>\n\t\tf<b>o</b>ob<b>a</b>r\n\t</baz>a\n</doc>'

    assert str(parse("<doc />")) == ""
    assert str(parse("<doc>I <b>love</b> you.</doc>")) == "I love you."
    assert parse("<doc>\nmom\nwow\n</doc>")[0].strip() == "mom\nwow"
    assert str(
        parse('<bing>  <bang> <bong>center</bong> </bang>  </bing>')
    ) == "center"
    assert str(parse('<doc>\xcf\x80</doc>')) == '\xcf\x80'

    d = Element(
        'foo',
        attrs={'foo': 'bar'},
        children=['hit with a', Element('bar'), Element('bar')]
    )

    try:
        d._doesnotexist
        assert False, "but found success. Damn."
    except AttributeError:
        pass
    assert d.bar._name == 'bar'
    try:
        d.doesnotexist
        assert False, "but found success. Damn."
    except AttributeError:
        pass

    assert hasattr(d, 'bar') is True

    assert d('foo') == 'bar'
    d(silly='yes')
    assert d('silly') == 'yes'
    assert d() == d._attrs

    assert d[0] == 'hit with a'
    d[0] = 'ice cream'
    assert d[0] == 'ice cream'
    del d[0]
    assert d[0]._name == "bar"
    assert len(d[:]) == len(d._dir)
    assert len(d[1:]) == len(d._dir) - 1
    assert len(d['bar',]) == 2
    d['bar',] = 'baz'
    assert len(d['bar',]) == 3
    assert d['bar']._name == 'bar'

    d = Element('foo')

    doc = Namespace("http://example.org/bar")
    bbc = Namespace("http://example.org/bbc")
    dc = Namespace("http://purl.org/dc/elements/1.1/")
    d = parse("""<doc version="2.7182818284590451"
        xmlns="http://example.org/bar"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:bbc="http://example.org/bbc">
        <author>John Polk and John Palfrey</author>
        <dc:creator>John Polk</dc:creator>
        <dc:creator>John Palfrey</dc:creator>
        <bbc:show bbc:station="4">Buffy</bbc:show>
    </doc>""")

    assert repr(d) == '<doc version="2.7182818284590451">...</doc>'
    assert d.__repr__(1) == (
        '<doc xmlns="http://example.org/bar" xmlns:bbc="http://example.org/bbc"'
        ' xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.71828182845904'
        '51"><author>John Polk and John Palfrey</author><dc:creator>John Polk</'
        'dc:creator><dc:creator>John Palfrey</dc:creator><bbc:show bbc:station='
        '"4">Buffy</bbc:show></doc>'
    )
    assert d.__repr__(1,1) == (
        '<doc xmlns="http://example.org/bar" xmlns:bbc="http://example.org/bbc"'
        ' xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.71828182845904'
        '51">\n\t<author>John Polk and John Palfrey</author>\n\t<dc:creator>Joh'
        'n Polk</dc:creator>\n\t<dc:creator>John Palfrey</dc:creator>\n\t<bbc:s'
        'how bbc:station="4">Buffy</bbc:show>\n</doc>'
    )

    assert repr(parse("<doc xml:lang='en' />")) == '<doc xml:lang="en"></doc>'

    assert str(d.author) == str(d['author']) == "John Polk and John Palfrey"
    assert d.author._name == doc.author
    assert str(d[dc.creator]) == "John Polk"
    assert d[dc.creator]._name == dc.creator
    assert str(d[dc.creator,][1]) == "John Palfrey"
    d[dc.creator] = "Me!!!"
    assert str(d[dc.creator]) == "Me!!!"
    assert len(d[dc.creator,]) == 1
    d[dc.creator,] = "You!!!"
    assert len(d[dc.creator,]) == 2

    assert d[bbc.show](bbc.station) == "4"
    d[bbc.show](bbc.station, "5")
    assert d[bbc.show](bbc.station) == "5"

    e = Element('e')
    e.c = '<img src="foo">'
    assert e.__repr__(1) == '<e><c>&lt;img src="foo"></c></e>'
    e.c = '2 > 4'
    assert e.__repr__(1) == '<e><c>2 > 4</c></e>'
    e.c = 'CDATA sections are <em>closed</em> with ]]>.'
    assert e.__repr__(1) == (
        '<e><c>CDATA sections are &lt;em>closed&lt;/em> with ]]&gt;.</c></e>'
    )
    e.c = parse(
        '<div xmlns="http://www.w3.org/1999/xhtml">i<br /><span></span>love<br'
        ' />you</div>'
    )
    assert e.__repr__(1) == (
        '<e><c><div xmlns="http://www.w3.org/1999/xhtml">i<br /><span></span>'
        'love<br />you</div></c></e>'
    )

    e = Element('e')
    e('c', 'that "sucks"')
    assert e.__repr__(1) == '<e c="that &quot;sucks&quot;"></e>'

    assert quote("]]>") == "]]&gt;"
    assert quote(
        '< dkdkdsd dkd sksdksdfsd fsdfdsf]]> kfdfkg >'
    ) == '&lt; dkdkdsd dkd sksdksdfsd fsdfdsf]]&gt; kfdfkg >'

    assert parse('<x a="&lt;"></x>').__repr__(1) == '<x a="&lt;"></x>'
    assert parse(
        '<a xmlns="http://a"><b xmlns="http://b"/></a>'
    ).__repr__(1) == '<a xmlns="http://a"><b xmlns="http://b"></b></a>'

    # This uses internal entities to DoS vulnerable XML parsers
    evil_xml = """<?xml version="1.0"?>
        <!DOCTYPE lolz [
         <!ENTITY lol "lol">
         <!ELEMENT lolz (#PCDATA)>
         <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
         <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
         <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
         <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
         <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
         <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
         <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
         <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
         <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
        ]>
        <lolz>&lol9;</lolz>"""
    try:
        assert parse(evil_xml)
        # It never gets here and instead raises a defusedxml.common.EntitiesForbidden exception
        assert False
    except defusedxml.common.EntitiesForbidden:
        assert True


if __name__ == '__main__':
    main_test()
