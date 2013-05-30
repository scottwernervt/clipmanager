#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import sys
from PySide import QtCore
from PySide import QtGui
from PySide import QtTest

sys.path.append('..')
from clipmanager import clipboards
import qspysignal

# Initialize qApp
try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    pass


class TestClipBoards(object):

    def setup_class(self):
        self.cb = clipboards.ClipBoards()

        self.mime_data = QtCore.QMimeData()
        self.text = 'hi'
        self.mime_data = QtCore.QMimeData()
        self.mime_data.setHtml('<b>' + self.text + '</b>')
        self.mime_data.setText('hi')

        self.connection_box = qspysignal.ConnectionBox()

    def test_emit_set_new_item(self):
        self.connection_box.connect(self.cb,
                                    QtCore.SIGNAL('new-item(QMimeData)'),
                                    self.connection_box.slotSlot)
        self.cb.emit_new_item(self.mime_data)

        self.connection_box.assertSignalArrived('new-item(QMimeData)')
        self.connection_box.assertNumberOfArguments(1)
        self.connection_box.assertArgumentTypes(QtCore.QMimeData)

    def _set_data(self):
        """Set QMimeData to clipboard."""
        self.cb.set_data(self.mime_data)

    def test_get_data(self):
        """Is the data set the same clipboard contents?"""
        self._set_data()
        assert self.cb.get_global_clipboard_data() == self.mime_data

    def test_get_data_has_formats(self):
        """Does the clipboard have format(s)?"""
        mime_data = self.cb.get_global_clipboard_data()
        assert mime_data.formats()
    
    def test_get_data_has_text(self):
        """Does the clipboard have plain text?"""
        mime_data = self.cb.get_global_clipboard_data()
        assert mime_data.hasText()

    def test_get_data_has_html(self):
        """Does the clipboard have html text?"""
        mime_data = self.cb.get_global_clipboard_data()
        assert mime_data.hasHtml()

    def test_get_owner(self):
        """Is python the owner of the clipboard?"""
        if sys.platform.startswith('win32'):
            proc_name = clipboards.get_win32_owner()
        elif sys.platform.startswith('linux'):
            proc_name = clipboards.get_x11_owner()

        assert len(proc_name) > 0

    def test_clear(self):
        """Does the clipboard contents get deleted?"""
        self.cb.clear()
        formats = self.cb.get_global_clipboard_data().formats()
        assert len(formats) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-vs'])