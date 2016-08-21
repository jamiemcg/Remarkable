#!usr/bin/python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
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

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
gi.require_version('WebKit', '3.0')

from bs4 import BeautifulSoup
from gi.repository import Gdk, Gtk, GtkSource, Pango, WebKit
from locale import gettext as _
from urllib.request import urlopen
import markdown
import os
import pdfkit
import re, subprocess, datetime, os, webbrowser, _thread, sys, locale
import tempfile
import traceback
import styles
import unicodedata
import warnings
import datetime


#Check if gtkspellcheck is installed
try:
    from gtkspellcheck import SpellChecker
    spellcheck_enabled = True
except:
    print("*Spellchecking not enabled.\n*To enable spellchecking install pygtkspellcheck\n*https://pypi.python.org/pypi/pygtkspellcheck/")
    spellcheck_enabled = False

import logging
logger = logging.getLogger('remarkable')

#Ignore warnings re. scroll handler (temp. fix) && starting GTK warning
warnings.filterwarnings("ignore", ".*has no handler with id.*")

from remarkable_lib import Window, remarkableconfig
from remarkable.AboutRemarkableDialog import AboutRemarkableDialog

app_version = 1.87 #Remarkable app version

class RemarkableWindow(Window):
    __gtype_name__ = "RemarkableWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(RemarkableWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutRemarkableDialog

        self.settings = Gtk.Settings.get_default()

        self.is_fullscreen = False
        self.editor_position = 0
        self.homeDir = os.environ['HOME']
        self.path = os.path.join(self.homeDir, ".remarkable/")
        self.settings_path = os.path.join(self.path, "remarkable.settings")
        self.media_path = remarkableconfig.get_data_path() + os.path.sep + "media" + os.path.sep
        
        self.name = "Untitled" #Title of the current file, set to 'Untitled' as default

        self.default_html_start = '<!doctype HTML><html><head><meta charset="utf-8"><title>Made with Remarkable!</title><link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/highlight.js/8.1/styles/github.min.css">'
        self.default_html_start += "<style type='text/css'>" + styles.css + "</style>"
        self.default_html_start += "</head><body id='MathPreviewF'>"
        self.default_html_end = '<script src="http://cdnjs.cloudflare.com/ajax/libs/highlight.js/8.1/highlight.min.js"></script><script>hljs.initHighlightingOnLoad();</script><script type="text/javascript" src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script><script type="text/javascript">MathJax.Hub.Config({"showProcessingMessages" : false,"messageStyle" : "none","tex2jax": { inlineMath: [ [ "$", "$" ] ] }});</script></body></html>'
        
        self.remarkable_settings = {}

        self.default_extensions = ['markdown.extensions.extra','markdown.extensions.toc', 'markdown.extensions.smarty', 'markdown.extensions.nl2br', 'markdown.extensions.urlize', 'markdown.extensions.Highlighting', 'markdown.extensions.Strikethrough', 'markdown.extensions.markdown_checklist', 'markdown.extensions.superscript', 'markdown.extensions.subscript', 'markdown.extensions.mathjax']
        self.safe_extensions = ['markdown.extensions.extra', 'markdown.extensions.nl2br']
        self.pdf_error_warning = False

        self.window = self.builder.get_object("remarkable_window")
        self.window.connect("delete-event", self.window_delete_event)
        self.window.connect("destroy", self.quit_requested)

        self.text_buffer = GtkSource.Buffer()
        self.text_view = GtkSource.View.new_with_buffer(self.text_buffer)
        self.text_view.set_show_line_numbers(True)
        self.text_view.set_auto_indent(True)
        
        # Force the SourceView to use a SourceBuffer and not a TextBuffer
        self.lang_manager = GtkSource.LanguageManager()
        self.text_buffer.set_language(self.lang_manager.get_language('markdown'))
        self.text_buffer.set_highlight_matching_brackets(True)
        
        self.undo_manager = self.text_buffer.get_undo_manager()
        self.undo_manager.connect("can-undo-changed", self.can_undo_changed)
        self.undo_manager.connect("can-redo-changed", self.can_redo_changed)

        self.text_buffer.connect("changed", self.on_text_view_changed)
        self.text_view.set_buffer(self.text_buffer)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)

        self.live_preview = WebKit.WebView()
        self.live_preview.connect("console-message", self._javascript_console_message) # Suppress .js output
        self.live_preview.zoom_out()

        self.scrolledwindow_text_view = Gtk.ScrolledWindow()
        self.scrolledwindow_text_view.add(self.text_view)
        self.scrolledwindow_live_preview = Gtk.ScrolledWindow()
        self.scrolledwindow_live_preview.add(self.live_preview)

        self.paned = self.builder.get_object("paned")
        self.paned.set_position(self.window.get_size()[0]/2)
        self.paned.pack1(self.scrolledwindow_text_view)
        self.paned.pack2(self.scrolledwindow_live_preview)

        self.toolbar = self.builder.get_object("toolbar")
        self.toolbutton_undo = self.builder.get_object("toolbutton_undo")
        self.toolbutton_undo.set_sensitive(False)
        self.toolbutton_redo = self.builder.get_object("toolbutton_redo")
        self.toolbutton_redo.set_sensitive(False)

        self.statusbar = self.builder.get_object("statusbar")
        self.context_id = self.statusbar.get_context_id("main status bar")

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.update_status_bar(self)
        self.update_live_preview(self)

        text = ""

        #Check if filename has been specified in terminal command
        if len(sys.argv) > 1:
            self.name = sys.argv[1]
            title = self.name.split("/")[-1]
            self.window.set_title("Remarkable: " + title)
            try:
                with open(sys.argv[1], 'r') as temp:
                    text = temp.read()
                    self.text_buffer.set_text(text)
                    self.text_buffer.set_modified(False)
            except:
                print(self.name + " does not exist, creating it")

        self.update_status_bar(self)
        self.update_live_preview(self)

        #Check if an updated version of application exists
        _thread.start_new_thread(self.check_for_updates, ())
        
        self.text_view.grab_focus()
        
        if spellcheck_enabled:
            try:
                self.spellchecker = SpellChecker(self.text_view, locale.getdefaultlocale()[0]) #Enabling spell checking
            except:
                pass #Spell checking not enabled

        self.tv_scrolled = self.scrolledwindow_text_view.get_vadjustment().connect("value-changed", self.scrollPreviewTo)
        self.lp_scrolled_fix = self.scrolledwindow_live_preview.get_vadjustment().connect("value-changed", self.scrollPreviewToFix)
        self.scrolledwindow_live_preview.get_vadjustment().set_lower(1)

        self.temp_file_list = []

    def can_redo_changed(self, widget):
        if self.text_buffer.can_redo():
            self.builder.get_object("menuitem_redo").set_sensitive(True)
            self.builder.get_object("toolbutton_redo").set_sensitive(True)
        else:
            self.builder.get_object("menuitem_redo").set_sensitive(False)
            self.builder.get_object("toolbutton_redo").set_sensitive(False)

    def can_undo_changed(self, widget):
        if self.text_buffer.can_undo():
            self.builder.get_object("menuitem_undo").set_sensitive(True)
            self.builder.get_object("toolbutton_undo").set_sensitive(True)

        else:
            self.builder.get_object("menuitem_undo").set_sensitive(False)
            self.builder.get_object("toolbutton_undo").set_sensitive(False)

    def check_settings(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not os.path.isfile(self.settings_path):
            self.remarkable_settings = {}
            self.remarkable_settings['css'] = '' 
            self.remarkable_settings['font'] = "Sans 10"  
            self.remarkable_settings['line-numbers'] = True
            self.remarkable_settings['live-preview'] = True
            self.remarkable_settings['nightmode'] = False       
            self.remarkable_settings['statusbar'] = True
            self.remarkable_settings['style'] = "github"
            self.remarkable_settings['toolbar'] = True
            self.remarkable_settings['vertical'] = False
            self.remarkable_settings['word-wrap'] = True                    
            settings_file = open(self.settings_path, 'w')
            settings_file.write(str(self.remarkable_settings))
            settings_file.close()
        else:
            settings_file = open(self.settings_path)
            self.remarkable_settings = eval(settings_file.read())
            settings_file.close()
            self.load_settings()

    def write_settings(self):
        settings_file = open(self.settings_path, 'w')
        settings_file.write(str(self.remarkable_settings))
        settings_file.close()

    def load_settings(self):
        self.custom_css = self.remarkable_settings['css'] #Load the custom css (don't auto enable)

        if self.remarkable_settings['nightmode']:
            # Enable night/dark mode on startup
            self.builder.get_object("menuitem_night_mode").set_active(True)
            self.on_menuitem_night_mode_activate(self)

        if self.remarkable_settings['word-wrap'] == False:
            # Disable word wrap on startup
            self.builder.get_object("menuitem_word_wrap").set_active(False)
            self.on_menuitem_word_wrap_activate(self)

        if self.remarkable_settings['live-preview'] == False:
            # Disable Live Preview on startup
            self.builder.get_object("menuitem_live_preview").set_active(False)

        if self.remarkable_settings['toolbar'] == False:
            # Hide the toolbar on startup
            self.on_menuitem_toolbar_activate(self)

        if self.remarkable_settings['statusbar'] == False:
            # Hide the statusbar on startup
            self.on_menuitem_statusbar_activate(self)
        
        # New settings, create them with default if they don't exist
        if "line-numbers" not in self.remarkable_settings:
            self.remarkable_settings['line-numbers'] = True
                
        if self.remarkable_settings['line-numbers'] == False:
            # Hide line numbers on startup
            self.builder.get_object("menuitem_line_numbers").set_active(False)

        if "vertical" not in self.remarkable_settings:
            self.remarkable_settings['vertical'] = False
            
        if self.remarkable_settings['vertical'] == True:
            # Switch to vertical layout
            self.builder.get_object("menuitem_vertical_layout").set_active(True)

        # Try to load the previously chosen font, may fail as font may not exist, ect.
        try:
            self.font = self.remarkable_settings['font']
            self.text_view.override_font(Pango.FontDescription(self.font))
        except:
            pass # Loading font failed --> leave at default font
            
        # Try to load the previously chosen style. May fail if so, ignore
        try:
            self.style = self.remarkable_settings['style']
            if self.style == "dark":
                styles.css = styles.dark
            elif self.style == "foghorn":
                styles.css = styles.foghorn
            elif self.style == "github":
                styles.css = styles.github
            elif self.style == "handwriting_css":
                styles.css = styles.handwriting_css
            elif self.style == "markdown":
                styles.css = styles.markdown
            elif self.style == "metro_vibes":
                styles.css = styles.metro_vibes
            elif self.style == "metro_vibes_dark":
                styles.css = styles.metro_vibes_dark
            elif self.style == "modern_css":
                styles.css = styles.modern_css
            elif self.style == "screen":
                styles.css = styles.screen
            elif self.style == "solarized_dark":
                styles.css = styles.solarized_dark
            elif self.style == "solarized_light":
                styles.css = styles.solarized_light
            elif self.style == "custom":
                styles.css = styles.custom_css
            else:
                print("Style key error")

            self.update_style(self)
            self.update_live_preview(self)
        except:
            print("Couldn't choose previously selected style")

    def scrollPreviewToFix(self, widget):
        self.scrolledwindow_live_preview.get_vadjustment().disconnect(self.lp_scrolled_fix)
        value = self.scrolledwindow_live_preview.get_vadjustment().get_value()
        if value == 0: #Fix
            self.scrollPreviewTo(self)
        else:
            pass #Something better?

    def scrollPreviewTo(self, widget):
        self.scrolledwindow_live_preview.get_vadjustment().disconnect(self.lp_scrolled_fix)
        value = self.scrolledwindow_text_view.get_vadjustment().get_value()
        upper_edit = self.scrolledwindow_text_view.get_vadjustment().get_upper()
        preview_upper = self.scrolledwindow_live_preview.get_vadjustment().get_upper()
        if value >= upper_edit - self.scrolledwindow_text_view.get_vadjustment().get_page_size():
            self.scrolledwindow_live_preview.get_vadjustment().set_value(preview_upper - self.scrolledwindow_live_preview.get_vadjustment().get_page_size())
        else:
            self.scrolledwindow_live_preview.get_vadjustment().set_value(value / upper_edit * preview_upper)
        self.lp_scrolled_fix = self.scrolledwindow_live_preview.get_vadjustment().connect("value-changed", self.scrollPreviewToFix)

    def on_menuitem_numbered_list_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            start_line = start.get_line()
            end_line = end.get_line()
            i = 1
            while (start_line <= end_line):
                temp_iter = self.text_buffer.get_iter_at_line(start_line)
                self.text_buffer.insert(temp_iter, str(i) + ". ")
                start_line += 1
                i += 1
        else:
            temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            line_number = temp_iter.get_line()
            start_iter = self.text_buffer.get_iter_at_line(line_number)
            self.text_buffer.insert(start_iter, "1. ")

    def on_menuitem_new_activate(self, widget):
        self.new(self)

    def on_toolbutton_new_clicked(self, widget):
        self.new(self)

    """
        Launches a new instance of Remarkable
    """
    def new(self, widget):
        subprocess.Popen("remarkable")

    def on_menuitem_open_activate(self, widget):
        self.open(self)

    def on_toolbutton_open_clicked(self, widget):
        self.open(self)

    """
        Opens a file for editing / viewing
    """
    def open(self, widget):
        start, end = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(start, end, False)
        
        self.window.set_sensitive(False)
        chooser = Gtk.FileChooserDialog(title="Open File", action=Gtk.FileChooserAction.OPEN, buttons=(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = chooser.run()

        if response == Gtk.ResponseType.OK:
            # The user has selected a file
            selected_file = chooser.get_filename()
            
            if len(text) == 0 and not self.text_buffer.get_modified():
                # Current file is empty. Load contents of selected file into this view
                
                self.text_buffer.begin_not_undoable_action()
                file = open(selected_file, 'r')
                text = file.read()
                file.close()
                self.name = chooser.get_filename()
                self.text_buffer.set_text(text)
                title = chooser.get_filename().split("/")[-1]
                self.window.set_title("Remarkable: " + title)
                self.text_buffer.set_modified(False)
                self.text_buffer.end_not_undoable_action()
            else:
                # A file is already open. Load the selected file in a new Remarkable process
                subprocess.Popen(["remarkable", selected_file])
        
        elif response == Gtk.ResponseType.CANCEL:
            # The user has clicked cancel
            pass

        chooser.destroy()
        self.window.set_sensitive(True)

    def check_for_save(self, widget):
        reply = False
        if self.text_buffer.get_modified():
            message = "Do you want to save the changes you have made?"
            dialog = Gtk.MessageDialog(self.window,
                                       Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                       Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO,
                                       message)
            dialog.set_title("Save?")

            if dialog.run() == Gtk.ResponseType.NO:
                reply = False
            else:
                reply = True
            dialog.destroy()
        return reply

    def on_menuitem_save_activate(self, widget):
        self.save(self)

    def on_toolbutton_save_clicked(self, widget):
        self.save(self)

    def save(self, widget):
        if self.name != "Untitled":
            file = open(self.name, 'w')
            text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
            file.write(text)
            file.close()
            title = self.name.split("/")[-1]
            self.text_buffer.set_modified(False)
            self.window.set_title("Remarkable: " + title)
        else:
            self.save_as(self)

    def on_menuitem_save_as_activate(self, widget, crap = ""):
        self.save_as(self)

    def save_as(self, widget):
        self.window.set_sensitive(False)
        chooser = Gtk.FileChooserDialog(title=None, action=Gtk.FileChooserAction.SAVE, buttons=(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        chooser.set_do_overwrite_confirmation(True)
        title = self.name.split("/")[-1]
        chooser.set_title("Save As: " + title)
        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            file = open(chooser.get_filename(), 'w')
            self.name = chooser.get_filename()
            text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
            file.write(text)
            file.close()
            self.text_buffer.set_modified(False)
            title = self.name.split("/")[-1]
            self.window.set_title("Remarkable: " + title)
        elif response == Gtk.ResponseType.CANCEL:
            pass
        chooser.destroy()
        self.window.set_sensitive(True)

    def on_menuitem_export_html_activate(self, widget):
        self.window.set_sensitive(False)
        start, end = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(start, end, False)
        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        try:
            html_middle = markdown.markdown(text, self.default_extensions)
        except:
            try:
                html_middle = markdown.markdown(text, extensions =self.safe_extensions)
            except:
                html_middle = markdown.markdown(text)
        html = self.default_html_start + html_middle + self.default_html_end
        self.save_html(html)

    def on_menuitem_export_html_plain_activate(self, widget):
        # This can be re-factored. A lot of duplicated code. Migrate some functions to external .py files
        self.window.set_sensitive(False)
        start, end = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(start, end, False)
        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        try:
            html_middle = markdown.markdown(text, self.default_extensions)
        except:
            try:
                html_middle = markdown.markdown(text, extensions =self.safe_extensions)
            except:
                html_middle = markdown.markdown(text)
        html = html_middle
        self.save_html(html)

    def save_html(self, data):
        html = data
        chooser = Gtk.FileChooserDialog("Export HTML", None, Gtk.FileChooserAction.SAVE,
                                        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                         Gtk.STOCK_OK, Gtk.ResponseType.OK))
        html_filter = Gtk.FileFilter()
        html_filter.set_name("HTML Files")
        html_filter.add_pattern("*.html")
        html_filter.add_pattern("*.htm")
        chooser.set_do_overwrite_confirmation(True)
        chooser.add_filter(html_filter)
        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            file_name = chooser.get_filename()
            if not file_name.endswith(".html"):
                file_name += ".html"
            file = open(file_name, 'w')
            soup = BeautifulSoup(html, "lxml")
            
            file.write(soup.prettify())
            file.close()
        elif response == Gtk.ResponseType.CANCEL:
            pass
        chooser.destroy()
        self.window.set_sensitive(True)

    def on_menuitem_export_pdf_activate(self, widget):
        self.window.set_sensitive(False)
        start, end = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(start, end, False)
        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        try:
            html_middle = markdown.markdown(text, self.default_extensions)
        except:
            try:
                html_middle = markdown.markdown(text, self.safe_extensions)
            except:
                html_middle = markdown.markdown(text)
        html = self.default_html_start + html_middle + self.default_html_end
        self.save_pdf(html)

    def on_menuitem_export_pdf_plain_activate(self, widget):
        self.window.set_sensitive(False)
        start, end = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(start, end, False)
        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        try:
            html_middle = markdown.markdown(text, self.default_extensions)
        except:
            try:
                html_middle = markdown.markdown(text, self.safe_extensions)
            except:
                html_middle = markdown.markdown(text)
        html = html_middle
        self.save_pdf(html)
        
    def save_pdf(self, html):
        chooser = Gtk.FileChooserDialog("Export PDF", None, Gtk.FileChooserAction.SAVE,
                                        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                         Gtk.STOCK_OK, Gtk.ResponseType.OK))
        pdf_filter = Gtk.FileFilter()
        pdf_filter.add_pattern("*.pdf")
        pdf_filter.set_name("PDF Files")
        chooser.add_filter(pdf_filter)
        chooser.set_do_overwrite_confirmation(True)
        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            file_name = chooser.get_filename()
            if not file_name.endswith(".pdf"):
                file_name += ".pdf"
            try:
                pdfkit.from_string(html, file_name, options= {'quiet': '', 'page-size': 'Letter',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                    'javascript-delay' : '550',
                    'no-outline': None})
            except:
                try:
                    #Failed so try with no options
                    pdfkit.from_string(html, file_name)
                except:
                    #Pdf Export failed, show warning message
                    if not self.pdf_error_warning:
                        self.pdf_error_warning = True
                        print("\nRemarkable Error:\tPDF Export Failed!!")

                    pdf_fail_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                            Gtk.ButtonsType.CANCEL, "PDF EXPORT FAILED")
                    pdf_fail_dialog.format_secondary_text(
                            "File export to PDF was unsuccessful.")
                    pdf_fail_dialog.run()
                    pdf_fail_dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            pass

        chooser.destroy()
        self.window.set_sensitive(True)


    def on_menuitem_quit_activate(self, widget):
        self.clean_up()
        self.window_delete_event(self)

    def window_delete_event(self, widget, callback=None):
        start, end = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(start, end, False)
        if len(text) > 0:
            if self.check_for_save(None):
                self.save(self)
        self.quit_requested(None)

    def quit_requested(self, widget, callback_data=None):
        self.clean_up() # Second time, just to be safe
        Gtk.main_quit()

    def on_menuitem_undo_activate(self, widget):
        self.undo(self)

    def on_toolbutton_undo_clicked(self, widget):
        self.undo(self)

    def undo(self, widget):
        if self.text_buffer.can_undo():
            self.text_buffer.undo()

    def on_menuitem_redo_activate(self, widget):
        self.redo(self)

    def on_toolbutton_redo_clicked(self, widget):
        self.redo(self)

    def on_toolbutton_zoom_in_clicked(self, widget):
        self.live_preview.zoom_in()
        self.scrollPreviewToFix(self)

    def on_toolbutton_zoom_out_clicked(self, widget):
        self.live_preview.zoom_out()
        self.scrollPreviewToFix(self)

    def redo(self, widget):
        if self.text_buffer.can_redo():
            self.text_buffer.redo()

    def on_menuitem_cut_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            self.clipboard.set_text(text, -1)
            self.text_buffer.delete(start, end)

    def on_menuitem_copy_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            self.clipboard.set_text(text, -1)

    def on_menuitem_paste_activate(self, widget):
        text = self.clipboard.wait_for_text()
        image = self.clipboard.wait_for_image()
        if text != None:
            if self.text_buffer.get_has_selection():
                start, end = self.text_buffer.get_selection_bounds()
                self.text_buffer.delete(start, end)
            self.text_buffer.insert_at_cursor(text)
        elif image != None:
            image_rel_path = 'imgs'
            if self.name == 'Untitled':
                # File not yet saved (i.e. we do not have path for the file)
                self.save(widget)
                assert self.name != 'Untitled'

            image_dir = os.path.join(os.path.dirname(self.name), image_rel_path)
            image_fname = datetime.datetime.now().strftime('%Y%m%d-%H%M%S.png')
            image_path = os.path.join(image_dir, image_fname)
            text = '![](%s/%s)' % (image_rel_path, image_fname)

            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            image.savev(image_path, 'png', [], [])

            if self.text_buffer.get_has_selection():
                start, end = self.text_buffer.get_selection_bounds()
                self.text_buffer.delete(start, end)

            self.text_buffer.insert_at_cursor(text)

    def on_menuitem_lower_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            text = text.lower()
            self.text_buffer.delete(start, end)
            self.text_buffer.insert_at_cursor(text)

    def on_menuitem_title_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            text = text.title()
            self.text_buffer.delete(start, end)
            self.text_buffer.insert_at_cursor(text)

    def on_menuitem_upper_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            text = text.upper()
            self.text_buffer.delete(start, end)
            self.text_buffer.insert_at_cursor(text)
            
    def on_menuitem_join_lines_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            self.text_buffer.join_lines(start, end)
        
    def on_menuitem_sort_lines_activate(self, widget):
        if self.text_buffer.get_has_selection():
            # Sort the selected lines
            start, end = self.text_buffer.get_selection_bounds()
            self.text_buffer.sort_lines(start, end, GtkSource.SortFlags.CASE_SENSITIVE, 0)
        else:
            # No selection active, sort all lines
            start, end = self.text_buffer.get_bounds()
            self.text_buffer.sort_lines(start, end, GtkSource.SortFlags.CASE_SENSITIVE, 0)

    def on_menuitem_sort_lines_reverse_activate(self, widget):
        if self.text_buffer.get_has_selection():
            # Sort the selected lines in reverse
            start, end = self.text_buffer.get_selection_bounds()
            self.text_buffer.sort_lines(start, end, GtkSource.SortFlags.REVERSE_ORDER, 0)
        else:
            # No selection active, sort all lines in reverse
            start, end = self.text_buffer.get_bounds()
            self.text_buffer.sort_lines(start, end, GtkSource.SortFlags.REVERSE_ORDER, 0)
    
    def on_menuitem_copy_all_activate(self, widget):
        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        try:
            text = markdown.markdown(text, self.default_extensions)
        except:
            try:
                html_middle = markdown.markdown(text, extensions =self.safe_extensions)
            except:
                html_middle = markdown.markdown(text)
        self.clipboard.set_text(text, -1)

    def on_menuitem_copy_selection_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            try:
                text = markdown.markdown(text, self.default_extensions)
            except:
                try:
                    html_middle = markdown.markdown(text, extensions =self.safe_extensions)
                except:
                    html_middle = markdown.markdown(text)
            self.clipboard.set_text(text, -1)

    def on_menuitem_vertical_layout_activate(self, widget):
        if self.builder.get_object("menuitem_vertical_layout").get_active():
            # Switch to vertical layout and need to reset position
            self.paned.set_orientation(Gtk.Orientation.VERTICAL)
            self.paned.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.paned.set_orientation(Gtk.Orientation.VERTICAL)
            self.paned.set_position(self.paned.get_allocation().height/2) 
            self.remarkable_settings['vertical'] = True
        else:   
            self.paned.set_orientation(Gtk.Orientation.HORIZONTAL)
            self.paned.set_position(self.paned.get_allocation().width/2)
            self.remarkable_settings['vertical'] = False
        self.write_settings()

    def on_menuitem_word_wrap_activate(self, widget):
        if self.builder.get_object("menuitem_word_wrap").get_active():
            self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
            self.remarkable_settings['word-wrap'] = True
        else:
            self.text_view.set_wrap_mode(Gtk.WrapMode.NONE)
            self.remarkable_settings['word-wrap'] = False   
        self.write_settings()


    def on_menuitem_line_numbers_activate(self, widget):
        if self.builder.get_object("menuitem_line_numbers").get_active():
            self.text_view.set_show_line_numbers(True)
            self.remarkable_settings['line-numbers'] = True
        else:
            self.text_view.set_show_line_numbers(False)
            self.remarkable_settings['line-numbers'] = False
        self.write_settings()
            
    def on_menuitem_live_preview_activate(self, widget):
        self.toggle_live_preview(self)

    def toggle_live_preview(self, widget):
        if self.live_preview.get_visible():
                # Hide the live preview
                self.paned.remove(self.scrolledwindow_live_preview)
                self.live_preview.set_visible(False)
                self.builder.get_object("menuitem_swap").set_sensitive(False)
                self.builder.get_object("menuitem_swap").set_tooltip_text("Enable Live Preview First")
                self.builder.get_object("toolbar1").set_visible(False)
                self.remarkable_settings['live-preview'] = False
        else:  # Show the live preview
            if self.editor_position == 0:
                self.paned.add(self.scrolledwindow_live_preview)
            else:
                self.paned.remove(self.scrolledwindow_text_view)
                self.paned.add(self.scrolledwindow_live_preview)
                self.paned.add(self.scrolledwindow_text_view)
            self.live_preview.set_visible(True)
            self.remarkable_settings['live-preview'] = True
            self.builder.get_object("menuitem_swap").set_sensitive(True)
            self.builder.get_object("menuitem_swap").set_tooltip_text("")
            self.builder.get_object("toolbar1").set_visible(True)
            self.update_live_preview(self)
        self.write_settings()


    def on_menuitem_swap_activate(self, widget):
        if self.live_preview.get_visible():
            self.paned.remove(self.scrolledwindow_live_preview)
            self.paned.remove(self.scrolledwindow_text_view)
            if self.editor_position == 0:
                self.paned.add(self.scrolledwindow_live_preview)
                self.paned.add(self.scrolledwindow_text_view)
                self.editor_position = 1
            else:
                self.paned.add(self.scrolledwindow_text_view)
                self.paned.add(self.scrolledwindow_live_preview)
                self.editor_position = 0
        else:
            pass # Do nothing as live preview is not visible

    def on_menuitem_editor_font_activate(self, widget):
        self.font_chooser = Gtk.FontSelectionDialog()
        self.font_chooser.set_preview_text("Remarkable is the best markdown editor for Linux")
        try:
            self.font_chooser.set_font_name(self.font)
        except:
            pass # Font not initialized, do nothing, continue
        self.font_chooser.connect("destroy", self.font_dialog_destroyed)
        self.font_ok_button = self.font_chooser.get_ok_button()
        self.font_ok_button.connect("clicked", self.font_dialog_ok)
        self.font_cancel_button = self.font_chooser.get_cancel_button()
        self.font_cancel_button.connect("clicked", self.font_dialog_cancel)
        self.font_chooser.show()

    def font_dialog_destroyed(self, widget):
        self.font_chooser.destroy()

    def font_dialog_cancel(self, widget):
        self.font_chooser.destroy()

    def font_dialog_ok(self, widget):
        self.font = self.font_chooser.get_font_name()
        self.remarkable_settings['font'] = self.font # Save prefs
        self.write_settings()    
        self.text_view.override_font(Pango.FontDescription(self.font))

        # Now adjust the size using TextTag
        self.font_dialog_destroyed(self)

    def on_menuitem_statusbar_activate(self, widget):
        if self.statusbar.get_visible():
            self.statusbar.set_visible(False)
            self.builder.get_object("menuitem_statusbar").set_label("Show Statusbar")
            self.remarkable_settings['statusbar'] = False
        else:
            self.statusbar.set_visible(True)
            self.update_status_bar(self)
            self.builder.get_object("menuitem_statusbar").set_label("Hide Statusbar")
            self.remarkable_settings['statusbar'] = True
        self.write_settings()

    def on_menuitem_toolbar_activate(self, widget):
        if self.toolbar.get_visible():
            self.toolbar.set_visible(False)
            self.builder.get_object("menuitem_toolbar").set_label("Show Toolbar")
            self.builder.get_object("toolbar1").set_visible(False)
            self.remarkable_settings['toolbar'] = False
        else:
            self.toolbar.set_visible(True)
            self.builder.get_object("menuitem_toolbar").set_label("Hide Toolbar")
            self.builder.get_object("toolbar1").set_visible(True)
            self.remarkable_settings['toolbar'] = True
        self.write_settings()

    def on_menuitem_preview_browser_activate(self, widget):
        # Create a temporary HTML file
        tf = tempfile.NamedTemporaryFile(delete = False)
        self.temp_file_list.append(tf)
        tf_name = tf.name

        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        try:
            html_middle = markdown.markdown(text, self.default_extensions)
        except:
            try:
                html_middle = markdown.markdown(text, extensions =self.safe_extensions)
            except:
                html_middle = markdown.markdown(text)
        html = self.default_html_start + html_middle + self.default_html_end
        tf.write(html.encode())
        tf.flush()
        
        # Load the temporary HTML file in the user's default browser
        webbrowser.open_new_tab(tf_name)

    def on_menuitem_night_mode_activate(self, widget):
        if self.builder.get_object("menuitem_night_mode").get_active():
            self.settings.set_property("gtk-application-prefer-dark-theme", True)
            self.remarkable_settings['nightmode'] = True
        else:
            self.settings.set_property("gtk-application-prefer-dark-theme", False)
            self.remarkable_settings['nightmode'] = False
        self.write_settings()

    def on_menuitem_fullscreen_activate(self, widget):
        if self.is_fullscreen:
            self.window.unfullscreen()
            self.is_fullscreen = False
            self.builder.get_object("menuitem_fullscreen").set_label("Fullscreen")
        else:
            self.window.fullscreen()
            self.is_fullscreen = True
            self.builder.get_object("menuitem_fullscreen").set_label("Exit fullscreen")

    def on_menuitem_bold_activate(self, widget):
        self.bold(self)

    def on_toolbutton_bold_clicked(self, widget):
        self.bold(self)

    def bold(self, widget):
        if not self.text_buffer.get_has_selection():  # Nothing has been selected, add **** and place cursor in middle
            self.text_buffer.insert_at_cursor("****")
            loc = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            loc.backward_chars(2)
            self.text_buffer.place_cursor(loc)
        else:  # Turn selection bold
            selection_bounds = self.text_buffer.get_selection_bounds()
            mark1 = self.text_buffer.create_mark(None, selection_bounds[0], False)
            mark2 = self.text_buffer.create_mark(None, selection_bounds[1], False)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark1), "**")
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark2), "**")

    def on_menuitem_italic_activate(self, widget):
        self.italic(self)

    def on_toolbutton_italic_clicked(self, widget):
        self.italic(self)

    def italic(self, widget):
        if not self.text_buffer.get_has_selection():  # Nothing has been selected, add ** and place cursor in middle
            self.text_buffer.insert_at_cursor("**")
            loc = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            loc.backward_chars(1)
            self.text_buffer.place_cursor(loc)
        else:  # Turn selection italic
            selection_bounds = self.text_buffer.get_selection_bounds()
            mark1 = self.text_buffer.create_mark(None, selection_bounds[0], False)
            mark2 = self.text_buffer.create_mark(None, selection_bounds[1], False)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark1), "*")
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark2), "*")

    def on_menuitem_strikethrough_activate(self, widget):
        self.strikethrough(self)

    def on_toolbutton_strikethrough_clicked(self, widget):
        self.strikethrough(self)

    def strikethrough(self, widget):
        if not self.text_buffer.get_has_selection():  # Nothing has been selected, add **** and place cursor in middle
            self.text_buffer.insert_at_cursor("~~~~")
            loc = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            loc.backward_chars(2)
            self.text_buffer.place_cursor(loc)
        else:  # Strikethrough selection
            selection_bounds = self.text_buffer.get_selection_bounds()
            mark1 = self.text_buffer.create_mark(None, selection_bounds[0], False)
            mark2 = self.text_buffer.create_mark(None, selection_bounds[1], False)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark1), "~~")
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark2), "~~")

    def on_menuitem_highlight_activate(self, widget):
        if not self.text_buffer.get_has_selection():  # Nothing has been selected, add ==== and place cursor in middle
            self.text_buffer.insert_at_cursor("====")
            loc = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            loc.backward_chars(2)
            self.text_buffer.place_cursor(loc)
        else:  # Highlight the selected text
            selection_bounds = self.text_buffer.get_selection_bounds()
            mark1 = self.text_buffer.create_mark(None, selection_bounds[0], False)
            mark2 = self.text_buffer.create_mark(None, selection_bounds[1], False)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark1), "==")
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark2), "==")

    def on_menuitem_superscript_activate(self, widget):
        if not self.text_buffer.get_has_selection():  # Nothing has been selected, add ^^ and place cursor in middle
            self.text_buffer.insert_at_cursor("^^")
            loc = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            loc.backward_chars(1)
            self.text_buffer.place_cursor(loc)
        else:  # Convert selection to superscript
            selection_bounds = self.text_buffer.get_selection_bounds()
            mark1 = self.text_buffer.create_mark(None, selection_bounds[0], False)
            mark2 = self.text_buffer.create_mark(None, selection_bounds[1], False)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark1), "^")
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark2), "^")

    def on_menuitem_subscript_activate(self, widget):
        if not self.text_buffer.get_has_selection():  # Nothing has been selected, add ~~ and place cursor in middle
            self.text_buffer.insert_at_cursor("~~")
            loc = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            loc.backward_chars(1)
            self.text_buffer.place_cursor(loc)
        else:  # Convert selection to subscript
            selection_bounds = self.text_buffer.get_selection_bounds()
            mark1 = self.text_buffer.create_mark(None, selection_bounds[0], False)
            mark2 = self.text_buffer.create_mark(None, selection_bounds[1], False)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark1), "~")
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(mark2), "~")

    def on_menuitem_block_quote_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()

            start_line = start.get_line()
            end_line = end.get_line()

            while start_line <= end_line:
                temp_iter = self.text_buffer.get_iter_at_line(start_line)
                self.text_buffer.insert(temp_iter, ">")
                start_line += 1
        else:
            temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            line_number = temp_iter.get_line()
            start_iter = self.text_buffer.get_iter_at_line(line_number)
            self.text_buffer.insert(start_iter, ">")

    def on_menuitem_code_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()

            start_line = start.get_line()
            end_line = end.get_line()

            while (start_line <= end_line):
                temp_iter = self.text_buffer.get_iter_at_line(start_line)
                self.text_buffer.insert(temp_iter, "\t")
                start_line += 1
        else:
            temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            line_number = temp_iter.get_line()
            start_iter = self.text_buffer.get_iter_at_line(line_number)
            self.text_buffer.insert(start_iter, "\t")

    def on_menuitem_bullet_list_activate(self, widget):
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            start_line = start.get_line()
            end_line = end.get_line()

            while (start_line <= end_line):
                temp_iter = self.text_buffer.get_iter_at_line(start_line)
                self.text_buffer.insert(temp_iter, "- ")
                start_line += 1

        else:
            temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
            line_number = temp_iter.get_line()
            start_iter = self.text_buffer.get_iter_at_line(line_number)
            self.text_buffer.insert(start_iter, "- ")

    def on_menuitem_heading_1_activate(self, widget):
        temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
        line_number = temp_iter.get_line()
        start_iter = self.text_buffer.get_iter_at_line(line_number)
        self.text_buffer.insert(start_iter, "#")

    def on_menuitem_heading_2_activate(self, widget):
        temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
        line_number = temp_iter.get_line()
        start_iter = self.text_buffer.get_iter_at_line(line_number)
        self.text_buffer.insert(start_iter, "##")

    def on_menuitem_heading_3_activate(self, widget):
        temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
        line_number = temp_iter.get_line()
        start_iter = self.text_buffer.get_iter_at_line(line_number)
        self.text_buffer.insert(start_iter, "###")

    def on_menuitem_heading_4_activate(self, widget):
        temp_iter = self.text_buffer.get_iter_at_mark(self.text_buffer.get_insert())
        line_number = temp_iter.get_line()
        start_iter = self.text_buffer.get_iter_at_line(line_number)
        self.text_buffer.insert(start_iter, "####")

    def on_menuitem_horizonatal_rule_activate(self, widget):
        if not self.text_buffer.get_has_selection():
            self.text_buffer.insert_at_cursor("\n***\n")
        else:  # Turn selection bold
            selection_bounds = self.text_buffer.get_selection_bounds()
            markR = self.text_buffer.create_mark(None, selection_bounds[1], False)
            self.text_buffer.insert(self.text_buffer.get_iter_at_mark(markR), "\n***\n")

    def on_menuitem_timestamp_activate(self, widget):
        self.insert_timestamp(self)

    def on_toolbutton_timestamp_clicked(self, widget):
        self.insert_timestamp(self)

    def insert_timestamp(self, widget):
        text = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p") + " "
        self.text_buffer.insert_at_cursor(text + "\n")
        self.text_view.grab_focus()

    def on_menuitem_image_activate(self, widget):
        self.insert_image(self)

    def on_toolbutton_image_clicked(self, widget):
        self.insert_image(self)

    def insert_image(self, widget):
        self.insert_window_image = Gtk.Window()
        self.insert_window_image.set_title("Insert Image")
        self.insert_window_image.set_resizable(True)
        self.insert_window_image.set_border_width(6)
        self.insert_window_image.set_default_size(300, 250)
        self.insert_window_image.set_position(Gtk.WindowPosition.CENTER)
        vbox = Gtk.VBox()
        label_alt_text = Gtk.Label("Alt Text:")
        self.entry_alt_text_i = Gtk.Entry()
        label_title = Gtk.Label("Title:")
        self.entry_title_i = Gtk.Entry()
        label_url = Gtk.Label("Path/Url:")
        self.entry_url_i = Gtk.Entry()
        vbox.pack_start(label_alt_text, self, False, False)
        vbox.pack_start(self.entry_alt_text_i, self, False, False)
        vbox.pack_start(label_title, self, False, False)
        vbox.pack_start(self.entry_title_i, self, False, False)
        vbox.pack_start(label_url, self, False, False)
        self.hbox_url = Gtk.HBox()
        self.hbox_url.pack_start(self.entry_url_i, self, True, False)
        self.path_file_button = Gtk.FileChooserButton(title= "Select an image")
        self.path_file_button.connect("file-set", self.file_chooser_button_clicked)
        self.hbox_url.pack_start(self.path_file_button, self, False, False)
        vbox.pack_start(self.hbox_url, self, False, False)
        button = Gtk.Button("Insert Image")
        vbox.pack_end(button, self, False, False)
        self.insert_window_image.add(vbox)
        self.insert_window_image.show_all()
        button.connect("clicked", self.insert_image_cmd, self.insert_window_image)

    def file_chooser_button_clicked(self, widget):
        filePath = widget.get_filename()
        self.entry_url_i.set_text(filePath)

    def insert_image_cmd(self, widget, window):
        if self.entry_url_i.get_text():
            if self.entry_title_i.get_text():
                if self.entry_alt_text_i.get_text():  # Fill alt_text with a space ( > 1 char required)
                    link = "![" + self.entry_alt_text_i.get_text() + "](" + self.entry_url_i.get_text()
                    link += '  "' + self.entry_title_i.get_text() + '")'
                    self.text_buffer.insert_at_cursor(link)
                else:
                    link = "![ ](" + self.entry_url_i.get_text()
                    link += '  "' + self.entry_title_i.get_text() + '")'
                    self.text_buffer.insert_at_cursor(link)
            else:
                link = "![" + self.entry_alt_text_i.get_text() + "](" + self.entry_url_i.get_text() + ") "
                self.text_buffer.insert_at_cursor(link)
        else:
            pass
        self.insert_window_image.hide()

    def on_menuitem_link_activate(self, widget):
        self.insert_link(self)

    def on_toolbutton_link_clicked(self, widget):
        self.insert_link(self)

    def insert_link(self, widget):
        self.insert_window_link = Gtk.Window()
        self.insert_window_link.set_title("Insert Link")
        self.insert_window_link.set_resizable(True)
        self.insert_window_link.set_border_width(6)
        self.insert_window_link.set_default_size(350, 250)
        self.insert_window_link.set_position(Gtk.WindowPosition.CENTER)
        vbox = Gtk.VBox()
        label_alt_text = Gtk.Label("Alt Text:")
        self.entry_alt_text = Gtk.Entry()
        label_url = Gtk.Label("Url:")
        self.entry_url = Gtk.Entry()
        vbox.pack_start(label_alt_text, self, False, False)
        vbox.pack_start(self.entry_alt_text, self, False, False)
        vbox.pack_start(label_url, self, False, False)
        vbox.pack_start(self.entry_url, self, False, False)
        button = Gtk.Button("Insert Link")
        vbox.pack_end(button, self, False, False)

        # Use highligted text as the default "alt text"
        if self.text_buffer.get_has_selection():
            start, end = self.text_buffer.get_selection_bounds()
            text = self.text_buffer.get_text(start, end, True)
            self.entry_alt_text.set_text(text)

        self.insert_window_link.add(vbox)
        self.insert_window_link.show_all()
        button.connect("clicked", self.insert_link_cmd, self.insert_window_link)

    def insert_link_cmd(self, widget, window):
        if self.entry_url.get_text():
            link = "[" + self.entry_alt_text.get_text() + "](" + self.entry_url.get_text() + ") "
            # Delete highlighted text before inserting the link
            if self.text_buffer.get_has_selection():
                start, end = self.text_buffer.get_selection_bounds()
                self.text_buffer.delete(start, end)
            self.text_buffer.insert_at_cursor(link)
        else:
            pass
        self.insert_window_link.hide()


    # Styles
    def update_style(self, widget):
        self.default_html_start = '<!doctype HTML><html><head><meta charset="utf-8"><title>Made with Remarkable!</title><link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/highlight.js/8.1/styles/github.min.css">'
        self.default_html_start += "<style type='text/css'>" + styles.css + "</style>"
        self.default_html_start += "</head><body>"

    def on_menuitem_dark_activate(self, widget):
        styles.css = styles.dark
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "dark"
        self.write_settings()

    def on_menuitem_foghorn_activate(self, widget):
        styles.css = styles.foghorn
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "foghorn"
        self.write_settings()

    def on_menuitem_github_activate(self, widget):
        styles.css = styles.github
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "github"
        self.write_settings()

    def on_menuitem_handwritten_activate(self, widget):
        styles.css = styles.handwriting_css
        self.update_style(self)
        self.update_live_preview(self)
        self.live_preview.zoom_in()
        self.remarkable_settings['style'] = "handwriting_css"
        self.write_settings()

    def on_menuitem_markdown_activate(self, widget):
        styles.css = styles.markdown
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "markdown"
        self.write_settings()

    def on_menuitem_metro_vibes_activate(self, widget):
        styles.css = styles.metro_vibes
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "metro_vibes"
        self.write_settings()

    def on_menuitem_metro_vibes_dark_activate(self, widget):
        styles.css = styles.metro_vibes_dark
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "metro_vibes_dark"
        self.write_settings()


    def on_menuitem_modern_activate(self, widget):
        styles.css = styles.modern_css
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "modern_css"
        self.write_settings()

    def on_menuitem_screen_activate(self, widget):
        styles.css = styles.screen
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "screen"
        self.write_settings()
    
    def on_menuitem_solarized_dark_activate(self, widget):
        styles.css = styles.solarized_dark
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "solarized_dark"
        self.write_settings()

    def on_menuitem_solarized_light_activate(self, widget):
        styles.css = styles.solarized_light
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "solarized_light"
        self.write_settings()

    ##Custom CSS
    def on_menuitem_custom_activate(self, widget):
        self.custom_window = Gtk.Window()
        self.custom_window.set_default_size(640, 480)
        self.custom_window.set_position(Gtk.WindowPosition.CENTER)
        self.custom_window.set_title("Custom CSS")

        self.custom_vbox = Gtk.VBox()
        self.custom_scroller = Gtk.ScrolledWindow()
        self.custom_button = Gtk.Button("Apply")
        self.custom_vbox.pack_end(self.custom_button, False, False, 0)
        self.custom_text_view = Gtk.TextView()
        self.custom_text_buffer = Gtk.TextBuffer()
        self.custom_text_buffer.set_text(self.custom_css)
        self.custom_text_view.set_buffer(self.custom_text_buffer)
        self.custom_scroller.add(self.custom_text_view)
        self.custom_vbox.pack_start(self.custom_scroller, True, True, 0)
        self.custom_window.add(self.custom_vbox)
        self.custom_window.show_all()
        self.custom_button.connect("clicked", self.apply_custom_css, self.custom_window, self.custom_text_buffer)

    def apply_custom_css(self, widget, window, tb):
        start, end = tb.get_bounds()
        self.custom_css = tb.get_text(start, end, False).replace("'", '"')
        styles.css = self.custom_css
        self.remarkable_settings['css'] = styles.css
        window.hide()
        self.update_style(self)
        self.update_live_preview(self)
        self.remarkable_settings['style'] = "custom"
        self.write_settings()
    ## End Custom CSS

    def on_menuitem_github_page_activate(self, widget):
        webbrowser.open_new_tab("https://github.com/jamiemcg/remarkable")
    
    def on_menuitem_reportbug_activate(self, widget):
        webbrowser.open_new_tab("https://github.com/jamiemcg/remarkable/issues")

    def on_menuitem_feedback_activate(self, widget):
        window_feedback = Gtk.Window()
        window_feedback.set_title("Feedback Form")
        window_feedback.set_default_size(640, 640)
        window_feedback.set_position(Gtk.WindowPosition.CENTER)
        feedback_browser = WebKit.WebView()
        feedback_browser.connect("console-message", self._javascript_console_message) # Suppress .js output
        feedback_scroller = Gtk.ScrolledWindow()
        feedback_scroller.add(feedback_browser)
        window_feedback.add(feedback_scroller)
        feedback_browser.open("https://jamiemcgowan.typeform.com/to/ng5Lhc")
        window_feedback.show_all()

    def on_menuitem_about_activate(self, widget):
        self.AboutDialog.show(self)

    def on_menuitem_markdown_tutorial_activate(self, widget):
        tutorial_path = self.media_path  + "MarkdownTutorial.md"
        subprocess.Popen(["remarkable", tutorial_path])

    def on_menuitem_homepage_activate(self, widget):
        webbrowser.open_new_tab("http://remarkableapp.github.io")

    def on_menuitem_donate_activate(self, widget):
        webbrowser.open_new_tab("http://remarkableapp.github.io/linux/donate")

    def on_menuitem_check_for_updates_activate(self, widget):
        _thread.start_new_thread(self.check_for_updates, (True,))

    def check_for_updates(self, show = False):
        try:
            update_check = urlopen("http://remarkableapp.github.io/latest")
            latest_version = float(update_check.readline())
            if app_version < latest_version:
                print("There is a new version avaiable")
                subprocess.Popen(['notify-send', "Remarkable: A new version of this app is avaiable"])
                update_check = urlopen("http://remarkableapp.github.io/change_log")
                md = update_check.read()
                html = markdown.markdown(md)
                if show:
                    webbrowser.open_new_tab("http://remarkableapp.github.io")
            else:
                if show:
                    subprocess.Popen(['notify-send', "Remarkable: You already have the latest version of this app available"])
                    print("You have the latest version of this app available")
        except:
            print("Warning: Remarkable could not connect to the internet to check for updates")

    def on_text_view_changed(self, widget):
        start, end = self.text_buffer.get_bounds()
        
        if self.statusbar.get_visible():
            self.update_status_bar(self)
        else:  # statusbar not present, don't need to update/count words, etc.
            pass
        if self.live_preview.get_visible():
            self.update_live_preview(self)
            self.scrollPreviewTo(self)

        else:  # Live preview not enabled, don't need to update the view
            pass

        # Update title to reflect changes
        if self.text_buffer.get_modified():
            title = self.window.get_title()
            if title[0] != "*":
                title = "*" + title
                self.window.set_title(title)

    """
        Update the text in the status bar. Displays the number of lines,
        words and characters. This approach is possible inefficient.
    """
    def update_status_bar(self, widget):
        self.statusbar.pop(self.context_id)
        lines = self.text_buffer.get_line_count()
        chars = self.text_buffer.get_char_count()
        words = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False).split()
        word_count = 0
        word_exceptions = ["#", "##", "###", "####", "#####", "######", "*", "**", "-", "+", "_", "/", "\\", "/", ":",
                           ";", "@", "'", "~", "(", ")", "[", "]", "{", "}", "((", "))", "+-", "-+", "/=", ".", "|",
                           "!", "!!", "!!!", "$", "", "%", "^", "&"]  # Exclude these from word count
        for w in words:
            if w not in word_exceptions:
                if not re.match('^[0-9]{1,3}$', w):
                    word_count += 1
        self.status_message = "Lines: " + str(lines) + ", " + "Words: " + str(word_count) + ", Characters: " + str(chars)
        self.statusbar.push(self.context_id, self.status_message)

    def update_live_preview(self, widet):
        text = self.text_buffer.get_text(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter(), False)
        try:
            html_middle = markdown.markdown(text, self.default_extensions)
        except:
            try:
                html_middle = markdown.markdown(text, extensions =self.safe_extensions)
            except:
                html_middle = markdown.markdown(text)
        html = self.default_html_start + html_middle + self.default_html_end

        # Update the display, supporting relative paths to local images
        self.live_preview.load_string(html, "text/html", "utf-8", "file://{}".format(os.path.abspath(self.name)))

    """
        This function suppresses the messages from the WebKit (live preview) console
    """
    def _javascript_console_message(self, view, message, line, sourceid):
        return True


    """
        This function deletes any temporary files that were created during execution
    """
    def clean_up(self):
        i = len(self.temp_file_list) - 1
        while i >= 0:
            os.remove(self.temp_file_list[0].name)
            del self.temp_file_list[0]
            i -= 1
