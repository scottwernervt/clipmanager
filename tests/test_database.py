#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import os
import sys
sys.path.append('..')

from PySide import QtCore
from PySide import QtGui
from PySide import QtSql

from clipmanager import database

# Initialize qApp
try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    pass

# Delete old database file
try:
    os.unlink('contents.db')
except Exception as err:
    pass


@pytest.fixture(scope='session')
def db(request):
    """Return database connection and close it at end of test."""
    conn = database.create_connection('')   # Create filename.db in test dir
    request.addfinalizer(conn.close)
    return conn

@pytest.mark.usefixtures('db')
class TestConn(object):

    def test_is_open(self, db):
        """Is the database created and open?"""
        assert db.open()

    def test_db_driver(self, db):
        """Is the database sqlite?"""
        assert db.driverName() == 'QSQLITE'


class TestTables(object):

    def test_create_tables(self):
        """Do both tables get created?"""
        assert database.create_tables()

    def test_recreating_tables(self):
        """If tables exist the query should not raise an error."""
        assert database.create_tables()

    def test_insert_main(self):
        """Does inserting into main table return a row #?"""
        row_id = database.insert_main(QtCore.QDateTime.currentMSecsSinceEpoch(),
                                      'Item 1 Short Title',
                                      'Item 1 Full Title',
                                      504268943)
        assert row_id != None
        assert type(row_id) == long

    def test_insert_mime(self):
        """Does inserting into data table return a row #?"""
        format = 'text/plain'
        mime_data = QtCore.QMimeData()
        mime_data.setData(format, 'test mime data')
        byte_data = QtCore.QByteArray(mime_data.data(format))
        
        row_id = database.insert_mime(1, format, byte_data)
        assert row_id != None
        assert type(row_id) == long

    def test_get_mime(self):
        """Does lookup of ID on Data table return a list of formats and 
        bytedata?
        """
        assert database.get_mime(parent_id=None) == []

        # [ [format, byte_data], ... ]
        mime_list = database.get_mime(parent_id=1)  
        assert mime_list != None                    # Should be a list
        assert type(mime_list[0][0]) == unicode     # format
        assert type(mime_list[0][1]) == QtCore.QByteArray  # byte_data

    def test_delete_main(self):
        """Does row # get deleted in Main table?"""
        assert database.delete_main(row_id=None) == False
        assert database.delete_main(row_id=1) == True
        assert database.delete_main(row_id=10000) == False

    def test_delete_mime(self):
        """Do all row's with parent_id get deleted?"""
        assert database.delete_mime(parent_id=None) == False
        assert database.delete_mime(parent_id=10000) == False
        assert database.delete_mime(parent_id=1) == True


if __name__ == '__main__':
    pytest.main([__file__, '-vs'])