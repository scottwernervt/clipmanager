import os
import sys

from PySide.QtCore import QMimeData, SIGNAL
from PySide.QtGui import QApplication

import qspysignal
from clipmanager.clipboard import (
    ClipboardManager,
)
from clipmanager import owner

try:
    app = QApplication(sys.argv)
except RuntimeError:
    pass


def text_mime_data():
    data = QMimeData()
    data.setText('text')
    return data


def html_mime_data():
    data = QMimeData()
    data.setHtml('<h1>text</h1>')
    return data


class TestClipBoardManager(object):

    def setup_class(self):
        self.clipboard_manager = ClipboardManager()
        self.connection_box = qspysignal.ConnectionBox()

        self.html_data = QMimeData()
        self.html_data.setHtml('<h1>text</h1>')

    def test_emit_new_item(self):
        self.connection_box.connect(self.clipboard_manager,
                                    SIGNAL('newItem(QMimeData)'),
                                    self.connection_box.slotSlot)
        self.clipboard_manager.emit_new_item(text_mime_data())

        self.connection_box.assertSignalArrived('newItem(QMimeData)')
        self.connection_box.assertNumberOfArguments(1)
        self.connection_box.assertArgumentTypes(QMimeData)

    def test_set_text(self):
        """Is the data set the same clipboard contents?"""
        text = text_mime_data()
        self.clipboard_manager.set_text(text)
        mime_data = self.clipboard_manager.get_primary_clipboard_text()
        assert mime_data.text() == text.text()

    def test_set_html(self):
        """Is the data set the same clipboard contents?"""
        html = html_mime_data()
        self.clipboard_manager.set_text(html)
        mime_data = self.clipboard_manager.get_primary_clipboard_text()
        assert mime_data.html() == html.html()

    def test_get_text_has_formats(self):
        """Does the clipboard have format(s)?"""
        text = text_mime_data()
        self.clipboard_manager.set_text(text)
        mime_data = self.clipboard_manager.get_primary_clipboard_text()
        assert mime_data.formats()

    def test_get_text_has_text(self):
        """Does the clipboard have plain text?"""
        text = text_mime_data()
        self.clipboard_manager.set_text(text)
        mime_data = self.clipboard_manager.get_primary_clipboard_text()
        assert mime_data.hasText()

    def test_get_text_has_html(self):
        """Does the clipboard have html text?"""
        html = html_mime_data()
        self.clipboard_manager.set_text(self.html_data)
        mime_data = self.clipboard_manager.get_primary_clipboard_text()
        assert mime_data.hasHtml()

    def test_clear_text(self):
        """Does the clipboard contents get deleted?"""
        self.clipboard_manager.clear_text()
        mime_data = self.clipboard_manager.get_primary_clipboard_text()
        assert mime_data.text() == ''

    def test_clipboard_owner(self):
        """Can we find the owner of the clipboard?"""
        window_owner = owner.initialize()
        window_names = window_owner()
        assert len(window_names) > 0
