### BEGIN LICENSE
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

import os
from gi.repository import Gtk

class RecentFilesMenu(object):
    def __init__(self, root_menu, files_list_path, max_files_num, file_choosen_callback = None):
        self.root_menu = root_menu
        self.files_list_path = files_list_path
        self.max_files_num = max_files_num
        self.file_choosen_callback = file_choosen_callback

    def __load_files_list(self):
        if not os.path.isfile(self.files_list_path):
            files_list = []
        else:
            file = open(self.files_list_path)
            files_list = eval(file.read())
            file.close()

        return files_list

    def __save_files_list(self, files_list):
        file = open(self.files_list_path, 'w')
        file.write(str(files_list))
        file.close()

    def __update_menu(self, files_list):
        if len(files_list) > 0:
            recent_submenu = Gtk.Menu()
            for file in files_list:
                title = file.split('/')[-1]
                menu_item = Gtk.MenuItem(title)
                menu_item.set_tooltip_text(file)
                menu_item.connect('activate', self.on_file_selected, file)

                recent_submenu.append(menu_item)

            self.root_menu.set_submenu(recent_submenu)
            self.root_menu.set_sensitive(True)
        else:
            self.root_menu.set_sensitive(False)

    def refresh(self):
        files_list = self.__load_files_list()
        self.__update_menu(files_list)

    def append_file(self, new_file_name):
        files_list = self.__load_files_list()

        #remove file name from the list if it is already in the list to avoid duplications
        if new_file_name in files_list:
            files_list.remove(new_file_name)

        #append file name at the beginning
        files_list.insert(0, new_file_name)

        if len(files_list) > self.max_files_num:
            files_list = files_list[:self.max_files_num]

        self.__save_files_list(files_list)

    def on_file_selected(self, widget, file_path):
        if self.file_choosen_callback != None:
            self.file_choosen_callback(file_path)
