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

try:
    app = QtGui.QApplication(sys.argv)
except RuntimeError:
    pass


def delete_temp_db():
	try:
		os.unlink('contents.db')
	except Exception as err:
		pass

MAIN_IDS = []
DATA_IDS = []

delete_temp_db()
db = database.create_connection('')


def test_create_connection():
	assert database.create_connection('') != False


def test_create_tables():
	database.create_tables()

	queries = ['SELECT * FROM Main', 'SELECT * FROM Data']
	for q in queries:
		query = QtSql.QSqlQuery()
		query.prepare(q)
		query.exec_()

		assert query.lastError().isValid() == False


def test_insert_main():
	date = QtCore.QDateTime.currentMSecsSinceEpoch()
	titleshort = 'Item 1 Short'
	titlefull = 'Item 1 Full'
	checksum = 504268943

	row_id = database.insert_main(date, titleshort, titlefull, checksum)
	MAIN_IDS.append(row_id)
	assert row_id != None
	assert type(row_id) == long


def test_insert_mime():
	parent_id = 1
	format = 'text/plain'
	mime_data = QtCore.QMimeData()
	mime_data.setData(format, 'test mime data ')
	byte_data = QtCore.QByteArray(mime_data.data(format))
	
	row_id = database.insert_mime(parent_id, format, byte_data)
	DATA_IDS.append(row_id)
	assert row_id != None
	assert type(row_id) == long


def test_get_mime():
	mime_list = database.get_mime(parent_id=1)
	assert mime_list != None
	assert type(mime_list) == list


def test_delete_main():
	assert database.delete_main(row_id=None) == False
	assert database.delete_main(row_id=1) == True
	assert database.delete_main(row_id=10000) == False

	test_insert_main()
	assert database.delete_main(row_id='2') == True


def test_delete_mime():
	assert database.delete_mime(parent_id=None) == False

	for id_ in DATA_IDS:
		assert database.delete_mime(parent_id=id_) == True

	assert database.delete_mime(parent_id=10000) == False


# Close database for test
db.close()
delete_temp_db()
app.exit()