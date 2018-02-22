import os
import zlib

import pytest
from PySide.QtCore import QDateTime, QMimeData, Qt

from clipmanager.database import Database
from clipmanager.models import DataSqlTableModel, MainSqlTableModel


@pytest.fixture()
def main_table():
    db = Database()
    db.create_tables()

    main = MainSqlTableModel()
    r = main.record()
    r.setValue('title', 'A')
    r.setValue('short_title', 'a')
    r.setValue('checksum', zlib.crc32('A'))
    r.setValue('created_at', QDateTime.currentMSecsSinceEpoch())
    if not main.insertRecord(-1, r):
        assert False

    main.submitAll()

    yield main

    db.close()
    os.unlink(db.connection.databaseName())


@pytest.fixture()
def data_table():
    db = Database()
    db.create_tables()

    data = DataSqlTableModel()

    mime_data = QMimeData()
    mime_data.setData('text/plain', 'plain-text')

    r = data.record()
    r.setValue('parent_id', 1)
    r.setValue('mime_format', 'text/plain')
    r.setValue('byte_data', mime_data.data('text/plain'))
    if not data.insertRecord(-1, r):
        assert False

    data.submitAll()

    yield data

    db.close()
    os.unlink(db.connection.databaseName())


class TestMainSqlTableModel:
    def test_create(self, main_table):
        row_id = main_table.create('title', 'short-title', 724990059,
                                   QDateTime.currentMSecsSinceEpoch())
        main_table.submitAll()

        assert row_id

    def test_data_display_role(self, main_table):
        index = main_table.index(0, main_table.TITLE)
        title = main_table.data(index.sibling(index.row(), main_table.TITLE),
                                role=Qt.DisplayRole)

        assert isinstance(title, unicode)
        assert title == 'A'

    def test_data_tooltip_role(self, main_table):
        index = main_table.index(0, main_table.TITLE_SHORT)
        tooltip = main_table.data(index.sibling(index.row(),
                                                main_table.TITLE_SHORT),
                                  role=Qt.ToolTipRole)

        assert isinstance(tooltip, str)
        assert 'last used' in tooltip.lower()


class TestDataSqlTableModel:
    def test_create(self, data_table):
        mime_data = QMimeData()
        mime_data.setData('text/plain', 'plain-text')
        byte_data = mime_data.data('plain-text')

        row_id = data_table.create(1, 'plain-text', byte_data)
        data_table.submitAll()

        assert row_id

    def test_read(self, data_table):
        mime_data = data_table.read(1)
        assert len(mime_data) > 0

        format_type = mime_data[0][0]
        byte_array = mime_data[0][1]

        mime_data = QMimeData()
        mime_data.setData(format_type, byte_array)

        assert format_type == 'text/plain'
        assert mime_data.text() == 'plain-text'

    def test_delete(self, data_table):
        data_table.delete([1])
        mime_data = data_table.read(1)

        assert len(mime_data) == 0
