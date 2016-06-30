#Library avaiable here: https://github.com/FND/markdown-checklist

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor


def makeExtension(configs=[]):
    return ChecklistExtension(configs=configs)


class ChecklistExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('checklist', ChecklistPostprocessor(md),
                '>raw_html')


class ChecklistPostprocessor(Postprocessor):
    """
    adds checklist class to list element
    """

    pattern = re.compile(r'<li>\[([ Xx])\]')

    def run(self, html):
        html = re.sub(self.pattern, self._convert_checkbox, html)
        before = '<ul>\n<li><input type="checkbox"'
        after = before.replace('<ul>', '<ul class="checklist">')
        return html.replace(before, after)

    def _convert_checkbox(self, match):
        state = match.group(1)
        checked = ' checked' if state != ' ' else ''
        return '<li><input type="checkbox" disabled%s>' % checked

