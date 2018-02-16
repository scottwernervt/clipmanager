import logging

from PySide.QtCore import QDateTime, Qt
from PySide.QtSql import QSqlQuery, QSqlTableModel

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
            time_stamp.setMSecsSinceEpoch(QSqlTableModel.data(self, date_index))
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

    def create(self, title, title_short, checksum, created_at):
        """Insert new row into the main table.

        :param title: Full title of clipboard contents.
        :type title: str

        :param title_short: Shorten title for truncating.
        :type title_short: str

        :param checksum: CRC32 checksum of entity.
        :type checksum: int

        :param created_at: UTC in milliseconds.
        :type created_at: int

        :return: Row id from SQL INSERT.
        :rtype: int
        """
        insert_query = QSqlQuery()
        insert_query.prepare('INSERT OR FAIL INTO main (title, title_short, '
                             'checksum, created_at) VALUES (:title, '
                             ':title_short, :checksum, :created_at)')
        insert_query.bindValue(':title', title)
        insert_query.bindValue(':title_short', title_short)
        insert_query.bindValue(':checksum', checksum)
        insert_query.bindValue(':created_at', created_at)
        insert_query.exec_()

        if insert_query.lastError().isValid():
            logger.error(insert_query.lastError().text())

        row_id = insert_query.lastInsertId()
        insert_query.finish()

        return row_id


class DataSqlTableModel(QSqlTableModel):
    ID, PARENT_ID, MIME_FORMAT, BYTE_DATA = range(4)

    def __init__(self, parent=None):
        super(DataSqlTableModel, self).__init__(parent)

        self.setTable('data')
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)

        self.select()

        self.setHeaderData(self.ID, Qt.Horizontal, 'id')
        self.setHeaderData(self.PARENT_ID, Qt.Horizontal, 'parent_id')
        self.setHeaderData(self.MIME_FORMAT, Qt.Horizontal, 'mime_format')
        self.setHeaderData(self.BYTE_DATA, Qt.Horizontal, 'byte_data')

    @staticmethod
    def create(parent_id, mime_format, byte_data):
        """Insert blob into the data table.

        :param parent_id: Row ID from main table.
        :type parent_id: int

        :param mime_format: Mime data format, i.e 'text/html'.
        :type mime_format: str

        :param byte_data: Mime data based on format converted to QByteArray.
        :type byte_data: QByteArray

        :return: Row ID from SQL INSERT.
        :rtype: int
        """
        insert_query = QSqlQuery()
        insert_query.prepare('INSERT OR FAIL INTO data VALUES (NULL, '
                             ':parent_id, :mime_format, :byte_data)')
        insert_query.bindValue(':parent_id', parent_id)
        insert_query.bindValue(':mime_format', mime_format)
        insert_query.bindValue(':byte_data', byte_data)
        insert_query.exec_()

        if insert_query.lastError().isValid():
            logger.error(insert_query.lastError().text())

        row_id = insert_query.lastInsertId()
        insert_query.finish()

        return row_id

    @staticmethod
    def read(parent_id):
        """Get blob from data table.

        :param parent_id: Main table row ID.
        :type parent_id: int

        :return: [['text/html','blob'],['text/plain','bytes']]
        :rtype: list[list[str,str]]
        """
        query = QSqlQuery()
        query.prepare('SELECT * FROM Data WHERE parent_id=:parent_id')
        query.bindValue(':parent_id', parent_id)
        query.exec_()

        mime_list = []  # [[mime_format, byte_data]]

        while query.next():
            mime_format = query.value(2)
            byte_data = query.value(3)
            mime_list.append([mime_format, byte_data])

            if query.lastError().isValid():
                logger.error(query.lastError().text())
                continue

        query.finish()
        return mime_list

    @staticmethod
    def delete(parent_ids):
        """Delete blob from data table.

        :param parent_ids: Row id of main table.
        :type parent_ids: list[int]

        :return: None
        :rtype: None
        """
        query = QSqlQuery()

        for parent_id in parent_ids:
            query.prepare('DELETE FROM data WHERE parent_id=:parent_id')
            query.bindValue(':parent_id', parent_id)

        query.exec_()

        if query.lastError().isValid():
            logger.error(query.lastError().text())

        query.finish()
