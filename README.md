# Remarkable

### A Fully Featured Markdown Editor for Linux

Remarkable is an open source Markdown Editor for Linux.
You can download the latest version from the [project site](https://remarkableapp.github.io/linux.html).
It is also available on the [AUR](https://aur.archlinux.org/packages/remarkable/).

![Remarkable](http://remarkableapp.github.io/images/main_screenshot.png)
![Remarkable Syntax Highlighting](http://remarkableapp.github.io/images/syntax_highlighting.png)

### Features

Remarkable has many features including:

- Live Preview with Synchronized Scrolling
- Syntax Highlighting
- GitHub Flavored Markdown Support
- HTML and PDF Export
- MathJax Support
- Dialogs for adding images, links and tables
- Styles
- Custom CSS Support
- Keyboard Shortcuts

Check out the [homepage](https://remarkableapp.github.io/linux.html) for more details and [screenshots](https://remarkableapp.github.io/linux/screenshots.html).

### Dependencies

Remarkable is a GTK 3 application: PyGObject and the GTK introspection stack are
provided by your distribution's packages, not by PyPI.

**Debian / Ubuntu**

`python3-gi gir1.2-gtk-3.0 gir1.2-gtksource-3.0 gir1.2-webkit2-4.1 gir1.2-glib-2.0 python3-bs4 python3-markdown python3-gtkspellcheck wkhtmltopdf`

**Fedora / RHEL**

`python3-gobject gtk3 gtksourceview3 webkit2gtk4.1 python3-beautifulsoup4 python3-markdown wkhtmltopdf`

With those installed, run it via uv. The virtualenv has to see the system GTK
bindings, so create it once with system site-packages:

```
uv venv --system-site-packages
uv run remarkable
```

On NixOS use the flake instead: `nix run`, or `nix develop` then `uv run remarkable`.

### Keyboard Shortcuts


|Action|Key|
|--|--|
|Bold|Ctrl+B|
|Copy|Ctrl+C|
|Cut|Ctrl+X|
|Export HTML|Ctrl+Shift+E|
|Export PDF|Ctrl+E|
|Find|Ctrl+F|
|Fullscreen|F11|
|Heading 1|Ctrl+1|
|Heading 2|Ctrl+2|
|Heading 3|Ctrl+3|
|Heading 4|Ctrl+4|
|Highlight|Ctrl+Shift+H|
|Insert Horizontal Rule|Ctrl+H|
|Insert Image|Ctrl+Shift+I|
|Insert Link|Ctrl+L|
|Insert Table|Ctrl+Shift+T|
|Insert Timestamp|Ctrl+T|
|Italic|Ctrl+I|
|New File|Ctrl+N|
|Open File|Ctrl+O|
|Paste|Ctrl+V|
|Quit|Ctrl+Q|
|Redo|Ctrl+Shift+Z|
|Save File|Ctrl+S|
|Save File As|Ctrl+Shift+S|
|Strikethrough|Ctrl+D|
|Undo|Ctrl+Z|
|Zoom In|Ctrl+Plus|
|Zoom Out|Ctrl+Minus|
