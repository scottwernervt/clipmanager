import logging

from PySide.QtCore import QDateTime, Qt
from PySide.QtSql import QSqlTableModel

from clipmanager.defs import CHECKSUM, CREATED_AT, ID, TITLE, TITLE_SHORT

logger = logging.getLogger(__name__)


class MainSqlTableModel(QSqlTableModel):
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

        # Call submitAll() to submit changes and update QListView
        # Necessary for handling max num of entries and date check
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)

        # Model view is only for Main table, not Data
        self.setTable('main')
        self.setSort(CREATED_AT, Qt.DescendingOrder)  # Sort by Date

        # Create header data
        self.setHeaderData(ID, Qt.Horizontal, 'ID')
        self.setHeaderData(TITLE, Qt.Horizontal, 'TITLE')
        self.setHeaderData(TITLE_SHORT, Qt.Horizontal, 'TITLE_SHORT')
        self.setHeaderData(CHECKSUM, Qt.Horizontal, 'CHECKSUM')
        self.setHeaderData(CREATED_AT, Qt.Horizontal, 'CREATED_AT')

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

    def data(self, index, role=Qt.DisplayRole):
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

        if role == Qt.DisplayRole and column == ID:
            return int(QSqlTableModel.data(self, index))

        if role == Qt.DisplayRole and column == TITLE:
            return unicode(QSqlTableModel.data(self, index))

        if role == Qt.DisplayRole and column == TITLE_SHORT:
            return unicode(QSqlTableModel.data(self, index))

        if role == Qt.DisplayRole and column == CREATED_AT:
            return int(QSqlTableModel.data(self, index))

        if role == Qt.DisplayRole and column == CHECKSUM:
            return unicode(QSqlTableModel.data(self, index))

        if role == Qt.ToolTipRole and column == TITLE_SHORT:
            date_index = self.index(row, CREATED_AT)

            time_stamp = QDateTime()
            time_stamp.setMSecsSinceEpoch(
                QSqlTableModel.data(self, date_index)
            )
            date_string = time_stamp.toString(Qt.SystemLocaleShortDate)
            return 'Last used: %s' % date_string

        # Used to display icons
        if role == Qt.DecorationRole:
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
            return Qt.ItemFlags()

        return Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
