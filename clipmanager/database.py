import logging
import os

from PySide.QtCore import QDir, QObject
from PySide.QtGui import QDesktopServices
from PySide.QtSql import QSqlDatabase, QSqlQuery

logger = logging.getLogger(__name__)


class Database(QObject):
    """Database connection helper.

    Database file can be found in:
    * Windows
    - XP: C:\Documents and Settings\<username>\Local Settings\Application Data\
    - 7/8: C:\Users\<username>\AppData\Local\Werner\ClipManager
    * Linux: /home/<username>/.local/share/data/Werner/ClipManager
    """
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

    def __init__(self, parent=None):
        super(Database, self).__init__(parent)

        storage_path = QDesktopServices.storageLocation(
            QDesktopServices.DataLocation)
        storage_dir = QDir(storage_path)
        if not storage_dir.exists():
            storage_dir.mkpath('.')

        db_path = os.path.join(storage_path, 'contents.db')
        logger.info(db_path)

        # noinspection PyTypeChecker,PyCallByClass
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(db_path)

        if not db.open():
            logger.error(db.lastError())

        self.connection = db

    def create_tables(self):
        """Create main and data table (one to many).

        :return: None
        :rtype: None
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

    def open(self):
        """Alias for QSqlDatabase.open()

        :return: True if connection open.
        :rtype: bool
        """
        return self.connection.open()

    def close(self):
        """Perform vacuum on database and then close.

        :return: None
        :rtype: None
        """
        query_data = QSqlQuery()
        query_data.exec_('VACUUM')
        query_data.finish()

        if query_data.lastError().isValid():
            logger.warning(query_data.lastError().text())

        self.connection.close()
