#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from PySide import QtCore
from PySide import QtSql

from defs import CHECKSUM
from defs import DATE
from defs import ID
from defs import TITLESHORT
from defs import TITLEFULL

logging.getLogger(__name__)


class MainSqlTableModel(QtSql.QSqlTableModel):
    """Main table model that has children in Data table.
    
    Todo:
        Look into returning Qt.UserRole+1, Qt.UserRole+n, for each column 
        instead of forcing me to create a new index requesting the specified 
        column. User role can be used on model().data(index, Qt.UserRole)

        Get PySide model test working.
        
        http://stackoverflow.com/questions/13055423/virtual-column-in-qtableview
    """
    def __init__(self, parent=None):
        super(MainSqlTableModel, self).__init__(parent)
        self.parent = parent
        
        # Model view is only for Main table, not Data
        self.setTable('Main')
        self.setSort(DATE, QtCore.Qt.DescendingOrder)   # Sort by Date

        # Create header data
        self.setHeaderData(ID, QtCore.Qt.Horizontal, 'ID')
        self.setHeaderData(DATE, QtCore.Qt.Horizontal, 'DATE')
        self.setHeaderData(TITLESHORT, QtCore.Qt.Horizontal, 'TITLESHORT')
        self.setHeaderData(TITLEFULL, QtCore.Qt.Horizontal, 'TITLEFULL')
        self.setHeaderData(CHECKSUM, QtCore.Qt.Horizontal, 'CHECKSUM')

        self.select()

    def select(self):
        """Subclass of select to disable lazy loading.

        References:
            http://qtsimplify.blogspot.com/2013/05/eager-loading.html

        Returns:
            bool: True/False
        """
        status = super(MainSqlTableModel, self).select()

        # Issue #1: QSortFilterProxyModel does not show all matching records 
        # due to all records not being loaded until scrolled.
        while self.canFetchMore():
            self.fetchMore()

        return status

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Subclass of data.

        Args:
            index (QModelIndex): Row and column of data entry.
            role: Qt.DisplayRole

        Returns:
            int: Integer from table.
            unicode: Text from table.
            None: No data found.
        """
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        if role == QtCore.Qt.DisplayRole and column == ID:
            return int(QtSql.QSqlTableModel.data(self, index))

        if role == QtCore.Qt.DisplayRole and column == TITLESHORT:
            return unicode(QtSql.QSqlTableModel.data(self, index))

        if role == QtCore.Qt.DisplayRole and column == TITLEFULL:
            return unicode(QtSql.QSqlTableModel.data(self, index))

        if role == QtCore.Qt.DisplayRole and column == DATE:
            return int(QtSql.QSqlTableModel.data(self, index))

        if role == QtCore.Qt.DisplayRole and column == CHECKSUM:
            return unicode(QtSql.QSqlTableModel.data(self, index))

        if role == QtCore.Qt.ToolTipRole and column == TITLESHORT:
            date_index = self.index(row, DATE)

            time_stamp = QtCore.QDateTime()
            time_stamp.setMSecsSinceEpoch(QtSql.QSqlTableModel.data(self, 
                                                                    date_index))
            date_string = time_stamp.toString(QtCore.Qt.SystemLocaleShortDate)
            return 'Last used: %s' % date_string

        # Used to display icons
        if role == QtCore.Qt.DecorationRole:
            return None

        return None

    def flags(self, index):
        """Return Qt flags for model.
        
        Called by the view to check the state of the items. Flags function 
        overides default from QAbstractListModel. How should we treat the items?

        Args:
            index (QModelIndex): Row and column of data entry.

        Returns:
            Qt.ItemFlags
        """
        if not index.isValid():
            return QtCore.Qt.ItemFlags()
        
        return QtCore.Qt.ItemFlags(QtCore.Qt.ItemIsEnabled | 
                                   QtCore.Qt.ItemIsSelectable)