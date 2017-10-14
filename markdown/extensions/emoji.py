### BEGIN LICENSE
# Copyright (C) 2017 <Harald Weiner> <harald.weiner@jku.at>
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

import markdown
import markdown.util
import os
import simplejson
import urllib3


# Global Vars
EMOJI_RE =r'(:{1})([a-zA-Z_\-\+0-9]+)\2' # the emoji is, e.g., :smile:

class EmojiPattern(markdown.inlinepatterns.Pattern):
    
    def __init__(self, RE, md):
        super().__init__(RE, md)
        dirname = os.path.dirname(os.path.realpath(__file__))
        my_filename = dirname + '/' + 'emoji.json'
        emoji = EmojiDict()
        #emoji.download_emoji_json_and_save_to(my_filename)
        content = emoji.read_emoji_json_file(my_filename)
        #print(content)
        self.emoji_dict = emoji.get_dict_from(content)
        #print(emoji_dict['smile'])

    """ Return an emoji image Element """
    def handleMatch(self, m):
        supr = m.group(3)
        text = supr
        src = 'https://assets-cdn.github.com/images/icons/emoji/unicode/'
        src += self.emoji_dict[text]
        el = markdown.util.etree.Element("img")
        el.set('alt', ':' + text + ':')
        el.set('height', '20')
        el.set('align', 'absmiddle')
        el.set('width', '20')
        el.set('src', src)
        el.text = ''
        return el

class Emoji(markdown.Extension):
    """ Emoji Extension for Python-Markdown. """
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['emoji'] = EmojiPattern(EMOJI_RE, md)

class EmojiDict():
    def download_emoji_json_and_save_to(self, filename):
        # project to which file belongs has MIT license
        url = 'https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json'
        urllib3.disable_warnings()
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        my_file = open(filename, 'wb')
        my_file.write(response.data)
        my_file.close()
        response.release_conn()

    def read_emoji_json_file(self, filename):
        my_file = open(filename, 'r')
        decoded=my_file.read()
        my_file.close()
        content = simplejson.loads(decoded)
        return content

    def get_dict_from(self, content):
        my_dict = {}
        for obj in content:
            #print(obj)
            name = obj['name']
            image = obj['image']
            #print(image)
            short_names = obj['short_names']
            for short_name in short_names:
                if short_name and image:
                    my_dict[short_name] = image
        return my_dict

def makeExtension(configs=[]):
    return Emoji(configs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
