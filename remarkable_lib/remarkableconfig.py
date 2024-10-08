# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2024 <Jamie McGowan> <jamiemcgowan.dev@gmail.com>
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

### DO NOT EDIT THIS FILE ###

__all__ = [
    'project_path_not_found',
    'get_data_file',
    'get_data_path',
    ]

# Where your project will look for your data
#(for instance, images and ui files).
__remarkable_data_directories__ = ['../data', '/usr/share/remarkable']
__license__ = 'MIT'
__version__ = '1.95'

import os

from locale import gettext as _

class project_path_not_found(Exception):
    """Raised when we can't find the project directory."""


def get_data_file(*path_segments):
    """Get the full path to a data file.

    Returns the path to a file underneath the data directory (as defined by
    `get_data_path`). Equivalent to os.path.join(get_data_path(),
    *path_segments).
    """
    return os.path.join(get_data_path(), *path_segments)


def get_data_path():
    """Retrieve remarkable data path

    This path is by default <remarkable_lib_path>/../data/ in trunk
    and /usr/share/remarkable in an installed version but this path
    is specified at installation time.
    """

    for data_dir in __remarkable_data_directories__:
        path = os.path.join(
            os.path.dirname(__file__), data_dir)

        abs_data_path = os.path.abspath(path)

        if os.path.exists(abs_data_path):
            return abs_data_path

    raise project_path_not_found


def get_version():
    return __version__
