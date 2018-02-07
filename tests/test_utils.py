#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sys

from PySide import QtCore

sys.path.append('..')
from clipmanager import utils


class TestCreateFullTitle(object):

    def setup_class(self):
        self.mime_plain_text = QtCore.QMimeData()
        self.plain_text = 'hi'
        self.mime_plain_text.setText(self.plain_text)

        self.mime_html = QtCore.QMimeData()
        self.html = '<b>' + self.plain_text + '</b>'
        self.mime_html.setHtml(self.html)

        self.mime_urls = QtCore.QMimeData()
        self.urls = [QtCore.QUrl('file://test1.txt'),
                     QtCore.QUrl('file://test2.txt')]
        self.mime_urls.setUrls(self.urls)

        self.mime_plain_html = QtCore.QMimeData()
        self.mime_plain_html.setText(self.plain_text)
        self.mime_plain_html.setHtml(self.html)

        self.mime_plain_html_urls = QtCore.QMimeData()
        self.mime_plain_html_urls.setText(self.plain_text)
        self.mime_plain_html_urls.setHtml(self.html)
        self.mime_plain_html_urls.setUrls(self.urls)

    def test_plain_text(self):
        assert utils.create_full_title(self.mime_plain_text) == self.plain_text

    def test_html_text(self):
        assert utils.create_full_title(self.mime_html) == self.html

    def test_urls(self):
        assert utils.create_full_title(self.mime_urls) != None

        for QUrl in self.urls:
            assert QUrl.toString() in utils.create_full_title(self.mime_urls)

    def test_plain_html(self):
        assert utils.create_full_title(self.mime_plain_html) == self.plain_text

    def test_plain_html_urls(self):
        for QUrl in self.urls:
            assert QUrl.toString() in utils.create_full_title(
                                                    self.mime_plain_html_urls)


class TestCalculateChecksum(object):

    def setup_class(self):
        self.mime_data = QtCore.QMimeData()

    def test_has_text(self):
        self.mime_data.setText('plain text')

        assert utils.calculate_checksum(self.mime_data) == -401376097

    def test_has_html(self):
        self.mime_data.setHtml('<b>html text</b>')

        assert utils.calculate_checksum(self.mime_data) == 1967596998

    def test_has_urls(self):
        urls = [QtCore.QUrl('file://test1.txt'),
                     QtCore.QUrl('file://test2.txt')]
        self.mime_data.setUrls(urls)

        assert utils.calculate_checksum(self.mime_data) == -478186416

    def test_unicode_text(self):
        self.mime_data.clear()

        unc = u'aaaàçççñññ' #  <type 'unicode'>
        self.mime_data.setText(unc)

        assert utils.calculate_checksum(self.mime_data) == -261852358

    def test_no_data(self):
        self.mime_data.clear()

        assert utils.calculate_checksum(self.mime_data) == None

    def test_unsupported_format(self):
        self.mime_data.clear()

        bytes = QtCore.QByteArray()
        bytes.resize(5)
        self.mime_data.setData('random/data', bytes)

        assert utils.calculate_checksum(self.mime_data) == None


def test_clean_up_text():
	assert utils.format_title('\ttab1') == 'tab1'
	assert utils.format_title('\tline1\n\t\tline2') == 'line1\n    line2'
	assert utils.format_title('    4 spaces') == '4 spaces'


def test_remove_extra_lines():
	assert utils.remove_extra_lines('Line1', 1) == 'Line1'
	assert utils.remove_extra_lines('Line1\nLine2', 1) == 'Line1...'
	assert utils.remove_extra_lines('Line1\nLine2\nLine3', 2) == 'Line1\nLine2...'


if __name__ == '__main__':
    pytest.main([__file__, '-vs'])