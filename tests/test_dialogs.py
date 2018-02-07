#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import sys

import clipmanager.ui.dialogs.preview
import clipmanager.ui.dialogs.settings

sys.path.append('..')

from PySide import QtCore
from PySide import QtGui
from PySide import QtWebKit
from PySide import QtTest

from clipmanager import dialogs

try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    pass


class TestSettingsDialog(object):

    def setup_class(self):
        self.dialog = clipmanager.ui.dialogs.settings.SettingsDialog()
        self.dialog.key_combo_edit.clear_text()
        self.dialog.super_check.setCheckState(QtCore.Qt.Unchecked)

    def test_key_combo_edit(self):
        # Test ESCAPE clearing edit contents
        self.dialog.key_combo_edit.setText('<RANDOM>')
        QtTest.QTest.keyClick(self.dialog.key_combo_edit, QtCore.Qt.Key_Escape)
        assert (self.dialog.key_combo_edit.text() == '')

        # Test converting modifiers to strings
        modifiers = {'<Ctrl>':  QtCore.Qt.Key_Control,
                     '<Shift>': QtCore.Qt.Key_Shift,
                     '<Alt>':   QtCore.Qt.Key_Alt}
        for key, value in modifiers.items():
            self.dialog.key_combo_edit.setText('')
            QtTest.QTest.keyClick(self.dialog.key_combo_edit, value)
            assert (self.dialog.key_combo_edit.text().lower() == key.lower())

        # Modifiers and keys conver to upper case
        key_combo = '<ctrl>f'
        self.dialog.key_combo_edit.setText(key_combo)
        assert (self.dialog.key_combo_edit.text() == key_combo.upper())

    def test_line_count_spin(self):
        # Minimum value
        minimum = self.dialog.line_count_spin.minimum()
        self.dialog.line_count_spin.setValue(minimum)
        self.dialog.line_count_spin.stepDown()
        assert (self.dialog.line_count_spin.value() == minimum)

        # Maximum value
        maximum = self.dialog.line_count_spin.maximum()
        self.dialog.line_count_spin.setValue(maximum)
        self.dialog.line_count_spin.stepUp()
        assert (self.dialog.line_count_spin.value() == maximum)

    def test_super_checkbox(self):
        self.dialog.key_combo_edit.clear_text()

        # Check <SUPER> is appended to 
        self.dialog.super_check.setCheckState(QtCore.Qt.Checked)
        assert (self.dialog.key_combo_edit.text() == '<SUPER>')

        # If unchecked return to stored hot key combo
        self.dialog.super_check.setCheckState(QtCore.Qt.Unchecked)
        assert (self.dialog.key_combo_edit.text() != '')

class TestPreviewDialog(object):

    def test_doc_plaintext(self):
        dialog = clipmanager.ui.dialogs.preview.PreviewDialog()

        # Plain text displays in QTextEdit
        mime_data = QtCore.QMimeData()
        mime_data.setText('hi')
        dialog.setup_ui(mime_data)

        assert (type(dialog.doc) == QtGui.QTextEdit)
        assert (len(dialog.doc.toPlainText()) > 0)
        del dialog

    def test_doc_html(self):
        dialog = clipmanager.ui.dialogs.preview.PreviewDialog()

        # Html text displays in QWebView
        text = 'hi'
        mime_data = QtCore.QMimeData()
        mime_data.setHtml('<b>' + text + '</b>')
        dialog.setup_ui(mime_data)

        assert (type(dialog.doc) == QtWebKit.QWebView)
        assert (dialog.doc.findText(text))
        del dialog

    def test_mix_mime(self):
        dialog = clipmanager.ui.dialogs.preview.PreviewDialog()

        # Html text displays in QWebView
        text = 'hi'
        mime_data = QtCore.QMimeData()
        mime_data.setHtml('<b>' + text + '</b>')
        mime_data.setText('hi')
        dialog.setup_ui(mime_data)

        assert (type(dialog.doc) == QtWebKit.QWebView)
        assert (dialog.doc.findText(text))
        del dialog


if __name__ == '__main__':
    pytest.main([__file__, '-vs'])