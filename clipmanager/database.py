import logging
import os

from PySide.QtCore import QObject
from PySide.QtSql import QSqlDatabase, QSqlQuery

logger = logging.getLogger(__name__)


class Database(QObject):
    _main_table_sql = """CREATE TABLE IF NOT EXISTS main(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        title_short TEXT,
        checksum TEXT,
        keep INTEGER DEFAULT 0,
        created_at TIMESTAMP
    );"""
    _data_table_sql = """CREATE TABLE IF NOT EXISTS data(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER,
        mime_format TEXT,
        byte_data BLOB,
        FOREIGN KEY(parent_id) REFERENCES main(id)
    );"""

    def __init__(self, storage_path, parent=None):
        super(Database, self).__init__(parent)

        db = QSqlDatabase.addDatabase('QSQLITE')

        db_path = os.path.join(storage_path, 'contents.db')
        logger.info(db_path)

        db.setDatabaseName(db_path)
        if not db.open():
            logger.error(db.lastError())

        self.connection = db

    @staticmethod
    def insert_main(title, title_short, checksum, created_at):
        """Insert new row into the main table.

        :param title: Full title of clipboard contents.
        :type title: str

        :param title_short: Shorten title for truncating.
        :type title_short: str

        :param checksum: CRC32 checksum of entity.
        :type checksum: str

        :param created_at: UTC in milliseconds.
        :type created_at: int

        :return: Row id from SQL INSERT.
        :rtype: int
        """
        insert_query = QSqlQuery()
        insert_query.prepare('INSERT OR FAIL INTO main (title, title_short, '
                             'checksum, created_at) VALUES (:title, :title_short, '
                             ':checksum, :created_at)')
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

    @staticmethod
    def delete_main(row_id):
        """Delete row from main table.

        :param row_id: Row id to delete.
        :type row_id: int

        :return: None
        :rtype: None
        """
        query = QSqlQuery()
        query.prepare('DELETE FROM main WHERE id=:id')
        query.bindValue(':id', row_id)
        query.exec_()

        if query.lastError().isValid():
            logger.error(query.lastError().text())

        query.finish()

    @staticmethod
    def insert_data(parent_id, mime_format, byte_data):
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
    def get_data(parent_id):
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
    def delete_data(parent_id):
        """Delete blob from data table.

        :param parent_id: Row id of main table.
        :type parent_id: int

        :return: None
        :rtype: None
        """
        query = QSqlQuery()
        query.prepare('DELETE FROM data WHERE parent_id=:parent_id')
        query.bindValue(':parent_id', parent_id)
        query.exec_()

        if query.lastError().isValid():
            logger.error(query.lastError().text())

        query.finish()

    def create_tables(self):
        """Create the tables: main and mime data.

        Main table has the following colums: ID, CREATED_AT, TITLE_SHORT, TITLE,
        and CHECKSUM. TITELSHORT is a truncated string based on lines to display
        setting. TITLE is the entire string used during proxy filter search.
        CHECKSUM is the cyclic redundancy check of the mime data QByteArray.
        """
        query_main = QSqlQuery()
        query_main.exec_(self._main_table_sql)
        query_main.finish()
        if query_main.lastError().isValid():
            logger.error(query_main.lastError().text())

        query_data = QSqlQuery()
        query_data.exec_(self._data_table_sql)
        query_data.finish()
        if query_data.lastError().isValid():
            logger.error(query_data.lastError().text())

        return True

    def close(self):
        self.connection.close()
