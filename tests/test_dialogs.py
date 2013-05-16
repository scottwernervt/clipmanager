#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import sys
sys.path.append('..')

from PySide import QtCore
from PySide import QtGui
from PySide import QtWebKit
from PySide import QtTest

from clipmanager import dialogs
# from clipmanager.settings import settings

try:
	app = QtGui.QApplication(sys.argv)
except RuntimeError:
	pass


class TestSettingsDialog(object):

	def setup_class(self):
		self.dialog = dialogs.SettingsDialog()
		self.dialog.key_combo_edit.clear()
		self.dialog.super_check.setCheckState(QtCore.Qt.Unchecked)

	def test_key_combo_edit(self):
		# Test ESCAPE clearing edit contents
		self.dialog.key_combo_edit.setText('<RANDOM>')
		QtTest.QTest.keyClick(self.dialog.key_combo_edit, QtCore.Qt.Key_Escape)
		assert (self.dialog.key_combo_edit.text() == '')

		# Test converting modifiers to strings
		modifiers = {'<Ctrl>': 	QtCore.Qt.Key_Control,
					 '<Shift>': QtCore.Qt.Key_Shift,
					 '<Alt>': 	QtCore.Qt.Key_Alt}
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
		self.dialog.key_combo_edit.clear()

		# Check <SUPER> is appended to 
		self.dialog.super_check.setCheckState(QtCore.Qt.Checked)
		assert (self.dialog.key_combo_edit.text() == '<SUPER>')

		# If unchecked return to stored hot key combo
		self.dialog.super_check.setCheckState(QtCore.Qt.Unchecked)
		assert (self.dialog.key_combo_edit.text() != '')


class TestAboutDialog(object):

	def setup_class(self):
		self.dialog = dialogs.AboutDialog()

	def test_licese_file_exits(self):
		assert os.path.exists('../clipmanager/license.txt')

	def test_license_textedit(self):
		assert (self.dialog.about_doc.toPlainText() != '')
		assert (len(self.dialog.about_doc.toPlainText()) > 0)


class TestPreviewDialog(object):

	def test_doc_plaintext(self):
		self.dialog = dialogs.PreviewDialog()

		# Plain text displays in QTextEdit
		mime_data = QtCore.QMimeData()
		mime_data.setText('hi')
		self.dialog.setup_ui(mime_data)

		assert (type(self.dialog.doc) == QtGui.QTextEdit)
		assert (len(self.dialog.doc.toPlainText()) > 0)
	
	def test_doc_html(self):
		self.dialog = dialogs.PreviewDialog()

		print self.dialog.setup_ui().item

		# Html text displays in QWebView
		text = 'hi'
		mime_data = QtCore.QMimeData()
		mime_data.setHtml('<b>' + text + '</b>')
		self.dialog.setup_ui(mime_data)

		assert (type(self.dialog.doc) == QtWebKit.QWebView)
		assert (self.dialog.doc.findText(text))
