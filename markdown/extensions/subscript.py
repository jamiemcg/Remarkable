#Modified verion of a library available here: https://github.com/sgraber/markdown.subscript

"""Subscript extension for Markdown.

To subscript something, place a tilde symbol, '~', before and after the
text that you would like in subscript:  C~6~H~12~O~6~
The numbers in this example will be subscripted.  See below for more:

Examples:

>>> import markdown
>>> md = markdown.Markdown(extensions=['subscript'])
>>> md.convert('This is sugar: C~6~H~12~O~6~')
u'<p>This is sugar: C<sub>6</sub>H<sub>12</sub>O<sub>6</sub></p>'

Paragraph breaks will nullify subscripts across paragraphs. Line breaks
within paragraphs will not.
"""

import markdown
from markdown.util import etree, AtomicString

# Global Vars
SUBSCRIPT_RE = r'(\~)([^\~]*)\2'  # the number is subscript~2~

class SubscriptPattern(markdown.inlinepatterns.Pattern):
    """ Return a subscript Element: `C~6~H~12~O~6~' """
    def handleMatch(self, m):
        subsc = m.group(3)
        
        text = subsc
        
        el = etree.Element("sub")
        el.text = AtomicString(text)
        return el

class SubscriptExtension(markdown.Extension):
    """ Subscript Extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Replace subscript with SubscriptPattern """
        md.inlinePatterns['subscript'] = SubscriptPattern(SUBSCRIPT_RE, md)

def makeExtension(configs=[]):
    return SubscriptExtension(configs=configs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
