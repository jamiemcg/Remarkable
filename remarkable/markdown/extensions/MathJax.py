import markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree

class MathJaxPattern(InlineProcessor):
    def __init__(self, pattern):
        super().__init__(pattern)

    def handleMatch(self, m, data):
        node = etree.Element("mathjax")

        delimiter = m.group(1)
        content = m.group(2)

        node.text = markdown.util.AtomicString(delimiter + content + delimiter)

        return node, m.start(0), m.end(0)

class MathJax(Extension):
    def extendMarkdown(self, md):
        mathjax_pattern = MathJaxPattern(r'(?<!\\)(\$\$?)(.+?)\1')
        md.inlinePatterns.register(mathjax_pattern, 'mathjax', 200)

def makeExtension(**kwargs):
    return MathJax(**kwargs)

