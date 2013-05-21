#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import random
import string
import sys
sys.path.append('..')

from PySide import QtCore
from PySide import QtGui
from PySide import QtTest

from clipmanager import view
import qspysignal

# Overwrite global variable ID
view.ID = 0
view.TITLESHORT = 0


try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    pass


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class SimpleListModel(QtCore.QAbstractListModel):
    def __init__(self, contents):
        super(SimpleListModel, self).__init__()
        self.contents = contents

    def removeRow(self, row):
        self.contents.pop(row)

    def rowCount(self, parent):
        return len(self.contents)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return str(self.contents[index.row()])


class TestListView(object):

    def setup_class(self):
        # Create model with random strings
        self.data = [str(id_generator(100)) for x in range(0,11)]
        self.model = SimpleListModel(self.data)

        # Create view
        self.view = view.ListView()
        self.view.setModel(self.model)
        self.view.show()    # Needed to test scrollbar
        
        self.connection_box = qspysignal.ConnectionBox()

    def select_item(self, row):
        index = self.view.model().index(row)

        selection_model = self.view.selectionModel()
        selection_model.select(index, QtGui.QItemSelectionModel.Select)
        selection_model.setCurrentIndex(index, QtGui.QItemSelectionModel.Select)

    def test_scrollbar_on(self):
        self.view.set_horiz_scrollbar(True)
        policy = self.view.horizontalScrollBarPolicy()
        assert (policy == QtCore.Qt.ScrollBarAlwaysOff)

    def test_scrollbar_off(self):
        self.view.set_horiz_scrollbar(False)
        policy = self.view.horizontalScrollBarPolicy()
        assert (policy == QtCore.Qt.ScrollBarAsNeeded)

    def key_arrow(self, key_direction):
        self.select_item(0)
        # selected_index = self.view.currentIndex()
        # rect = self.view.rectForIndex(selected_index)

        prior = self.view.horizontalScrollBar().value()
        # QtTest.QTest.mouseClick(self.view.viewport(), QtCore.Qt.LeftButton, 0, 
        #                         rect.center())
        QtTest.QTest.keyPress(self.view, key_direction)
        current = self.view.horizontalScrollBar().value()
        
        return (prior != current)

    def test_right_arrow(self):
        assert self.key_arrow(QtCore.Qt.Key_Right)

    def test_left_arrow(self):
        assert self.key_arrow(QtCore.Qt.Key_Left)

    def test_select_all(self):
        selection_model = self.view.selectionModel()
        QtTest.QTest.keyPress(self.view, QtCore.Qt.Key_A,
                              QtCore.Qt.ControlModifier)

        selection_count = len(selection_model.selectedIndexes())
        model_count = self.view.model().rowCount(None)

        assert (selection_count == model_count)

    def test_emit_set_clipboard(self):
        self.connection_box.connect(self.view,
                                    QtCore.SIGNAL('set-clipboard()'),
                                    self.connection_box.slotSlot)
        self.view._emit_set_clipboard()

        self.connection_box.assertSignalArrived('set-clipboard()')
        self.connection_box.assertNumberOfArguments(0)
        self.connection_box.assertArgumentTypes()

    def test_emit_open_settings(self):
        self.connection_box.connect(self.view,
                                    QtCore.SIGNAL('open-settings()'),
                                    self.connection_box.slotSlot)
        self.view._emit_open_settings()

        self.connection_box.assertSignalArrived('open-settings()')
        self.connection_box.assertNumberOfArguments(0)
        self.connection_box.assertArgumentTypes()

    def test_emit_open_preview(self):
        self.connection_box.connect(self.view,
                                    QtCore.SIGNAL('open-preview(QModelIndex)'),
                                    self.connection_box.slotSlot)
        self.view._emit_open_preview()

        self.connection_box.assertSignalArrived('open-preview(QModelIndex)')
        self.connection_box.assertNumberOfArguments(1)
        self.connection_box.assertArgumentTypes(QtCore.QModelIndex)

    def test_delete_rows(self):
        num_of_rows = self.view.model().rowCount(None)

        self.select_item(1)
        self.view._delete_rows()
        assert (len(self.data) < num_of_rows) 