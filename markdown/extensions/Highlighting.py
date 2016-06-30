### BEGIN LICENSE
# Copyright (C) 2016 <Jamie McGowan> <jamiemcgowan.dev@gmail.com>
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
### END LICENSE

from markdown.inlinepatterns import SimpleTagPattern
from markdown.extensions import Extension

reg_pattern =r'(={2})([^\?]+?)(={2})'  

class Highlighting(Extension): 
    def extendMarkdown(self, md, md_globals):
        """Modifies inline patterns."""
        mark_tag = SimpleTagPattern(reg_pattern, 'mark')
        md.inlinePatterns.add('mark', mark_tag, '_begin')
        
def makeExtension(configs=[]):
    return Highlighting(configs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
