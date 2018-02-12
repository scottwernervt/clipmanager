from PySide.QtCore import QDateTime, Qt
from PySide.QtSql import (
    QSqlRelation,
    QSqlRelationalTableModel,
    QSqlTableModel,
)


class MainSqlTableModel(QSqlTableModel):
    """Main table model that has children in Data table.
    
    Todo:
        Look into returning Qt.UserRole+1, Qt.UserRole+n, for each column 
        instead of forcing me to create a new index requesting the specified 
        column. User role can be used on model().data(index, Qt.UserRole)

        Get PySide model test working.
        
        http://stackoverflow.com/questions/13055423/virtual-column-in-qtableview
    """
    ID, TITLE, TITLE_SHORT, CHECKSUM, KEEP, CREATED_AT = range(6)

    def __init__(self, parent=None):
        super(MainSqlTableModel, self).__init__(parent)

        self.setTable('main')
        self.setSort(self.CREATED_AT, Qt.DescendingOrder)
        # submitAll() to make changes, needed for max entries / date check
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)

        self.select()

        self.setHeaderData(self.ID, Qt.Horizontal, 'id')
        self.setHeaderData(self.TITLE, Qt.Horizontal, 'title')
        self.setHeaderData(self.TITLE_SHORT, Qt.Horizontal, 'title_short')
        self.setHeaderData(self.CHECKSUM, Qt.Horizontal, 'checksum')
        self.setHeaderData(self.CREATED_AT, Qt.Horizontal, 'created_at')

    def select(self):
        """Load all records before returning if there is a selection.

        QSortFilterProxyModel does not show all matching records due to
        records not being loaded until scrolled.

        References:
        http://qtsimplify.blogspot.com/2013/05/eager-loading.html

        :return:
        :rtype: bool
        """
        while self.canFetchMore():
            self.fetchMore()

        return super(MainSqlTableModel, self).select()

    def data(self, index, role=Qt.DisplayRole):
        """Override QSqlTableModel.data()

        :param index: Row and column of data entry.
        :type index: QModelIndex

        :param role:
        :type role: Qt.DisplayRole

        :return: Row column data from table.
        :rtype: str, int, or None
        """
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        if role == Qt.DisplayRole and column == self.ID:
            return int(QSqlTableModel.data(self, index))

        if role == Qt.DisplayRole and column == self.TITLE:
            return unicode(QSqlTableModel.data(self, index))

        if role == Qt.DisplayRole and column == self.TITLE_SHORT:
            return unicode(QSqlTableModel.data(self, index))

        if role == Qt.DisplayRole and column == self.CREATED_AT:
            return int(QSqlTableModel.data(self, index))

        if role == Qt.DisplayRole and column == self.CHECKSUM:
            return unicode(QSqlTableModel.data(self, index))

        if role == Qt.ToolTipRole and column == self.TITLE_SHORT:
            date_index = self.index(row, self.CREATED_AT)

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
        """Return item's Qt.ItemFlags in history list view.

        :param index: Row and column of data entry.
        :type index: QModelIndex

        :return:
        :rtype: Qt.ItemFlags
        """
        if not index.isValid():
            return Qt.ItemFlags()

        return Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)


class DataSqlRelationalTableModel(QSqlRelationalTableModel):
    ID, PARENT_ID, MIME_FORMAT, BYTE_DATA = range(4)

    def __init__(self, parent=None):
        super(DataSqlRelationalTableModel, self).__init__(parent)

        self.setTable('data')
        self.setRelation(self.PARENT_ID,
                         QSqlRelation('main', 'id', 'mime_format'))
        self.select()
