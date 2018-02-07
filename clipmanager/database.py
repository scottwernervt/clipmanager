import logging
import os

from PySide.QtSql import QSqlDatabase, QSqlQuery

logger = logging.getLogger(__name__)

_main_table_sql = """CREATE TABLE IF NOT EXISTS Main(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TIMESTAMP,
    title_short      TEXT,
    title_full       TEXT,
    checksum        STRING,
    save            INTEGER DEFAULT 0
);"""

_data_table_sql = """CREATE TABLE IF NOT EXISTS Data(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id    INTEGER,
    format      STRING,
    data        BLOB
);"""

_main_table_alter_v3_sql = """
ALTER TABLE Main ADD COLUMN save INTEGER DEFAULT 0;
"""


def create_connection(storage_path):
    """Create sqlite connection.

    Args:
        storage_path (str): Absolute path to save contents.db.

    Returns:
        db (QSqlDatabase): Databe object.
        False: Database failed to open. QtSql driver missing or read 
               permissions on storage path.

    """
    db = QSqlDatabase.addDatabase('QSQLITE')

    db_path = os.path.join(storage_path, 'contents.db')
    db.setDatabaseName(db_path)

    if not db.open():
        logger.error(db.lastError())
        return False

    return db


def create_tables():
    """Create the tables: main and mime data.

    Main table has the following colums: ID, DATE, TITLE_SHORT, TITLE_FULL,
    and CHECKSUM. TITELSHORT is a truncated string based on lines to display
    setting. TITLE_FULL is the entire string used during proxy filter search.
    CHECKSUM is the cyclic redundancy check of the mime data QByteArray.
    """
    query_main = QSqlQuery()
    query_main.exec_(_main_table_sql)
    query_main.finish()
    if query_main.lastError().isValid():
        logger.error(query_main.lastError().text())
        return False

    query_main = QSqlQuery()
    query_main.exec_(_main_table_alter_v3_sql)
    query_main.finish()

    query_data = QSqlQuery()
    query_data.exec_(_data_table_sql)
    query_data.finish()
    if query_data.lastError().isValid():
        logger.error(query_data.lastError().text())
        return False

    return True


# def count_main():
#     query = QSqlQuery()
#     query.prepare('SELECT Count(*) FROM Main')

#     query.exec_()
#     query.next()

#     count = query.value(0)
#     if query.lastError().isValid():
#         logger.error(query.lastError().text())
#         count = 0

#     return count


def insert_main(date, title_short, title_full, checksum):
    """Insert new row into Main table.

    Args:
        date (long): The number of milliseconds since 1970-01-01T00:00:00 UTC.
        title_short (str): Truncated plain text based on number of lines to
            display.
        title_full (str): Entire plain text string.
        checksum (str): Checksum from CRC32.

    Returns:
        row_id (int): Row ID from SQL INSERT.
        None: Insert failed, see query.lastError().
    """
    query = QSqlQuery()
    query.prepare('INSERT OR FAIL INTO Main (date, title_short, title_full, '
                  'checksum) VALUES (:date, :title_short, :title_full, '
                  ':checksum)')
    query.bindValue(':date', date)
    query.bindValue(':title_short', title_short)
    query.bindValue(':title_full', title_full)
    query.bindValue(':checksum', checksum)
    query.exec_()

    if query.lastError().isValid():
        logger.error(query.lastError().text())

    row_id = query.lastInsertId()  # If failed: None
    logger.info('ID: %s' % row_id)

    query.finish()

    return row_id


def insert_mime(parent_id, format, byte_data):
    """Insert mime data into Data table.

    Stores Main table's parent id, mime format type, and mime blob into Data
    table.

    Args:
        parent_id (int): Row ID from Main table.
        format (str): Mime data format, i.e 'text/html'.
        byte_data (QByteArray): Mime data based on format converted to 
            QByteArray.

    Returns:
        row_id (int): Row ID from SQL INSERT.
    """
    query = QSqlQuery()
    query.prepare('INSERT OR FAIL INTO Data '
                  'VALUES (Null, :parent_id, :format, :data)')
    query.bindValue(':parent_id', parent_id)
    query.bindValue(':format', format)
    query.bindValue(':data', byte_data)
    query.exec_()

    if query.lastError().isValid():
        logger.error(query.lastError().text())

    row_id = query.lastInsertId()  # If failed: None
    logger.info('Parent_id-ChildID: %s-%s' % (parent_id, row_id))

    query.finish()

    return row_id


def delete_main(row_id):
    """Delete row from Main table.

    Number of rows affected by delete is outputted to log.

    Args:
        row_id (int): Row id in Main table.
    """
    query = QSqlQuery()
    query.prepare('DELETE FROM Main WHERE ID=:rowid')
    query.bindValue(':rowid', row_id)
    query.exec_()

    if query.lastError().isValid():
        logger.error(query.lastError().text())
        return False

    rows_affected = query.numRowsAffected()
    query.finish()

    logger.info('ID: %s' % row_id)
    logger.info('Rows: %s' % rows_affected)

    if rows_affected != 0:
        return True
    else:
        return False


def delete_mime(parent_id):
    """Delete mime data from Data table based on parent ID from Main table.

    Args:
        parent_id (int): Main table row ID.
    """
    query = QSqlQuery()
    query.prepare('DELETE FROM Data WHERE parent_id=:parent_id')
    query.bindValue(':parent_id', parent_id)
    query.exec_()

    if query.lastError().isValid():
        logger.error(query.lastError().text())

    rows_affected = query.numRowsAffected()
    query.finish()

    logger.info('ID: %s' % parent_id)
    logger.info('Rows: %s' % rows_affected)

    if rows_affected != 0:
        return True
    else:
        return False


def get_mime(parent_id):
    """Retrieve parent ID's mime data from Data table.

    Executes SELECT * FROM query based on parent id. Each row is this processed
    and combined into a list with the following format: [[format, bytedata]].

    Args:
        parent_id (int): Main table row ID.

    Returns:
        mime_list (list): [['text/html','blob'],['text/plain','bytes']]
    """
    logger.info('ID: %s' % parent_id)

    query = QSqlQuery()
    query.prepare('SELECT * FROM Data WHERE parent_id=:parent_id')
    query.bindValue(':parent_id', parent_id)
    query.exec_()

    mime_list = []  # [ [format, byte_data] ]
    while query.next():
        mime_format = query.value(2)
        byte_data = query.value(3)
        mime_list.append([mime_format, byte_data])

        if query.lastError().isValid():
            logger.error(query.lastError().text())
            return None

    query.finish()

    return mime_list
