# Copyright (C) 2002-2009 Stephen Kennedy <stevek@gnome.org>
# Copyright (C) 2012-2014 Kai Willadsen <kai.willadsen@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GtkSource # pylint: disable=E0611
from gi.repository import Gdk


class FindBar(object):
    def __init__(self, widget, wrap_box, find_entry, replace_entry,
                 match_case, whole_word, regex):
        self.widget = widget
        self.set_text_view(None)
        self.wrap_box = wrap_box
        self.find_entry = find_entry
        self.replace_entry = replace_entry
        # self.arrow_left.show()
        # self.arrow_right.show()

        settings = GtkSource.SearchSettings()
        match_case.bind_property('active', settings, 'case-sensitive')
        whole_word.bind_property('active', settings, 'at-word-boundaries')
        regex.bind_property('active', settings, 'regex-enabled')
        self.find_entry.bind_property('text', settings, 'search-text')
        settings.set_wrap_around(True)
        self.search_settings = settings
        self.widget.connect('key-press-event', self.on_find_bar_key_press)
        self.find_entry.connect('key-press-event', self.on_find_entry_key_press)
        self.find_entry.connect('key-release-event', self.on_find_entry_key_release)

    def on_focus_child(self, container, widget):
        if widget is not None:
            visible = self.widget.props.visible
            if widget is not self.widget and visible:
                self.hide()
        return False

    def on_find_bar_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide()

    def on_find_entry_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self._find_text(backwards=self.is_searching_backwards)
        elif event.keyval == Gdk.KEY_Shift_R or event.keyval == Gdk.KEY_Shift_L:
            self.is_searching_backwards = True
        elif event.keyval == Gdk.KEY_Escape:
            self.hide()

    def on_find_entry_key_release(self, widget, event):
        if event.keyval == Gdk.KEY_Shift_R or event.keyval == Gdk.KEY_Shift_L:
            self.is_searching_backwards = False

    def hide(self):
        #self.set_text_view(None)
        self.wrap_box.set_visible(False)
        self.widget.hide()

    def show(self):
        #self.set_text_view(None)
        self.wrap_box.set_visible(True)
        self.find_entry.grab_focus()
        self.widget.show()

    def set_text_view(self, textview):
        self.textview = textview
        if textview is not None:
            self.search_context = GtkSource.SearchContext.new(
                textview.get_buffer(), self.search_settings)
            self.search_context.set_highlight(True)
        else:
            self.search_context = None

    def start_find(self, textview, text=None):
        self.set_text_view(textview)
        self.replace_label.hide()
        self.replace_entry.hide()
        self.hbuttonbox2.hide()
        self.find_entry.get_style_context().remove_class("not-found")
        if text:
            self.find_entry.set_text(text)
        self.widget.set_row_spacing(0)
        self.widget.show()
        self.find_entry.grab_focus()

    def start_find_next(self, textview):
        self.set_text_view(textview)
        if self.find_entry.get_text():
            self.on_find_next_button_clicked(self.find_next_button)
        else:
            self.start_find(self.textview)

    def start_find_previous(self, textview, text=None):
        self.set_text_view(textview)
        if self.find_entry.get_text():
            self.on_find_previous_button_clicked(self.find_previous_button)
        else:
            self.start_find(self.textview)

    def start_replace(self, textview, text=None):
        self.set_text_view(textview)
        self.find_entry.get_style_context().remove_class("not-found")
        if text:
            self.find_entry.set_text(text)
        self.widget.set_row_spacing(6)
        self.widget.show_all()
        self.find_entry.grab_focus()
        self.wrap_box.set_visible(False)

    def on_find_next_button_clicked(self, button):
        self._find_text()

    def on_find_previous_button_clicked(self, button):
        self._find_text(backwards=True)

    def on_replace_button_clicked(self, entry):
        buf = self.textview.get_buffer()
        oldsel = buf.get_selection_bounds()
        match = self._find_text(0)
        newsel = buf.get_selection_bounds()

        # Only replace if there is an already-selected match at the cursor
        if (match and oldsel and oldsel[0].equal(newsel[0]) and
                oldsel[1].equal(newsel[1])):
            self.search_context.replace(
                newsel[0], newsel[1], self.replace_entry.get_text(), -1)
            self._find_text(0)

    def on_replace_all_button_clicked(self, entry):
        buf = self.textview.get_buffer()
        saved_insert = buf.create_mark(
            None, buf.get_iter_at_mark(buf.get_insert()), True)
        self.search_context.replace_all(self.replace_entry.get_text(), -1)
        if not saved_insert.get_deleted():
            buf.place_cursor(buf.get_iter_at_mark(saved_insert))
            self.textview.scroll_to_mark(
                buf.get_insert(), 0.25, True, 0.5, 0.5)

    def on_hide_panel_button_clicked(self, entry):
            self.hide()

    def on_find_entry_changed(self, entry):
        self.find_entry.get_style_context().remove_class("not-found")
        self._find_text(0)

    def _find_text(self, start_offset=1, backwards=False):
        assert self.textview
        assert self.search_context
        buf = self.textview.get_buffer()
        insert = buf.get_iter_at_mark(buf.get_insert())

        start, end = buf.get_bounds()
        self.wrap_box.set_visible(False)
        if not backwards:
            insert.forward_chars(start_offset)
            match, start_iter, end_iter = self.search_context.forward(insert)
            if match and (start_iter.get_offset() < insert.get_offset()):
                self.wrap_box.set_visible(True)
        else:
            match, start_iter, end_iter = self.search_context.backward(insert)
            if match and (start_iter.get_offset() > insert.get_offset()):
                self.wrap_box.set_visible(True)
        if match:
            buf.place_cursor(start_iter)
            buf.move_mark(buf.get_selection_bound(), end_iter)
            self.textview.scroll_to_mark(
                buf.get_insert(), 0.25, True, 0.5, 0.5)
            self.find_entry.get_style_context().remove_class("not-found")
            return True
        else:
            buf.place_cursor(buf.get_iter_at_mark(buf.get_insert()))
            self.find_entry.get_style_context().add_class("not-found")
            self.wrap_box.set_visible(False)
