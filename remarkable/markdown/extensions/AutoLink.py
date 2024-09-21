import markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re

# Define the URL pattern (e.g. google.com, http://example.com, etc.)
URL_REGEX = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'

class AutoLinkPattern(InlineProcessor):
    def __init__(self, pattern):
        super().__init__(pattern)

    def handleMatch(self, m, data):
        if m:  # Ensure match exists
            url = m.group(0)  # The entire matched URL

            # If the URL doesn't have a scheme (e.g. http or https), add 'http://'
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            # Create an <a> element
            el = etree.Element('a')
            el.set('href', url)
            el.text = markdown.util.AtomicString(m.group(0))  # The original URL text

            # Return the element and the start/end position of the match
            return el, m.start(0), m.end(0)
        
        # Always return a tuple (None, None, None) in case of no match
        return None, None, None

class AutoLink(Extension):
    def extendMarkdown(self, md):
        # Add the AutoLinkPattern to the markdown inline patterns
        autolink_pattern = AutoLinkPattern(URL_REGEX)
        # Register it with priority 150 so it runs before other patterns like emphasis
        md.inlinePatterns.register(autolink_pattern, 'autolink', 150)

# Factory function to create the extension
def makeExtension(**kwargs):
    return AutoLink(**kwargs)

# Example usage:
if __name__ == "__main__":
    text = "Here is a link: google.com and another one http://example.com"
    md = markdown.Markdown(extensions=[AutoLinkExtension()])
    html = md.convert(text)
    print(html)
