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

    def create_tables(self):
        """Create main and data table (one to many)."""
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

    def close(self):
        query_data = QSqlQuery()
        query_data.exec_('VACUUM')
        query_data.finish()

        if query_data.lastError().isValid():
            logger.warning(query_data.lastError().text())

        self.connection.close()
