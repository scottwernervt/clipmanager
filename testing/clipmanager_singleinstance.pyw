#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging.config
logging.config.fileConfig('logging.conf')

import ctypes
import os
import platform
import sys
import zlib

from PySide import (
	QtCore
	, QtGui
	, QtNetwork
	, QtDeclarative
)

import config
import clipboards
import database
import globalkeybinder
import history
from settings import settings
from settingsdialog import SettingsDialog
from searchbox import SearchBox
from systemtray import SystemTrayIcon


class ClipboardApp(QtGui.QApplication):
	""" Single instance: https://gitorious.org/qsingleapplication/qsingleapplication/blobs/master/qSingleApplication.py
	"""
	def __init__(self, parent=None):        
		super(ClipboardApp, self).__init__(parent)
		# Prevent dialog from exiting app if main window not visible
		self.setQuitOnLastWindowClosed(False) 

		self.main_window = MainWindow()

		# Connect quit message to call cleanup
		self.connect(self, QtCore.SIGNAL('aboutToQuit()'), self.cleanUpAtQuit)

	def singleStart(self):
		""" Open socket 
		"""
		self.m_socket = QtNetwork.QLocalSocket()
		self.m_socket.connected.connect(self.connectToExistingApp)
		self.m_socket.error.connect(self.startApplication)
		self.m_socket.connectToServer(self.applicationName(), QtCore.QIODevice.WriteOnly)
   
	def connectToExistingApp(self):
		if len(sys.argv)>1 and sys.argv[1] is not None:
			self.m_socket.write(sys.argv[1])
			self.m_socket.bytesWritten.connect(self.quit)
		else:
			QtGui.QMessageBox.critical(None, self.tr("Already running"), self.tr("The program is already running. Please check the system tray."))
			QtCore.QTimer.singleShot(250, self.quit)

	def startApplication(self):
		self.m_server = QtNetwork.QLocalServer()
		if self.m_server.listen(self.applicationName()):
			self.m_server.newConnection.connect(self.getNewConnection)

			# Load prior position saved if open at last position option
			# selected
			if (settings.getOpenWindowAt == 1) and \
				(settings.getWindowPos() is not None):
				self.main_window.move(settings.getWindowPos())

			# Load prior window size
			if settings.getWindowSize() is not None:
				self.main_window.resize(settings.getWindowSize())

			self.main_window.show()
		else:
			pass
			# QMessageBox.warning(None, self.tr("Warning"), self.tr("There might be another instance of the program running. In your process manager, please kill process!"))
	
	def getNewConnection(self):
		self.new_socket = self.m_server.nextPendingConnection()
		self.new_socket.readyRead.connect(self.readSocket)

	def readSocket(self):
		f = self.new_socket.readLine()
		self.main_window.getArgsFromOtherInstance(str(f))
		self.main_window.activateWindow()
		self.main_window.show()

	def cleanUpAtQuit(self):
		logging.debug('Exit Requested.')

		try:
			self.m_server.close()
		except AttributeError as err:
			logging.warn(err)

		# The basic concept behind this is that by default copying something into the clipboard 
		# only copies a reference/pointer to the source application. Then when another application 
		# wants to paste the data from the clipboard it requests the data from the source application.
		clipboard = QtGui.QApplication.clipboard()
		event = QtCore.QEvent(QtCore.QEvent.Clipboard)
		QtGui.QApplication.sendEvent(clipboard, event)

		self.main_window.cleanUp()
		logging.debug('Exiting...')


class MainWindow(QtGui.QMainWindow):

	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.parent = parent

		# Settings dialog
		self.settings_dialog = SettingsDialog(self)

		# Prevent user from changing window size
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.setWindowIcon(QtGui.QIcon(config._icon))
		self.setWindowTitle('Clipboard Manager')
		self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)

		# Connect, create, an get database contents
		self.db = database.createConnection()
		database.createTables()

		# Create Main Window
		self.main_widget = MainWidget(self) 
		self.setCentralWidget(self.main_widget)

		self.key_binder = globalkeybinder.SystemWrapper(self)
		self.key_binder.bind(settings.getGlobalHotKey(), self.toggleWindow)

		# Create system tray icon
		if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
			QMessageBox.critical(None, 'Systray', 'Cannot find a system tray.')
			logging.error('Cannot find a system tray.')
			sys.exit(1)

		self.tray_icon = SystemTrayIcon(self)
		self.tray_icon.activated.connect(self.iconActivated)
		self.tray_icon.show()

	def cleanUp(self):
		logging.debug('Unbinding global hot key.')
		self.key_binder.unbind(settings.getGlobalHotKey())

		logging.debug('Saving window size and position.')
		settings.setWindowPos(self.pos())
		settings.setWindowSize(self.size())

		logging.debug('Submitting changes to database.')
		self.main_widget.model_main.submitAll()
		
		logging.debug('Closing database.')
		self.db.close()

		return True

	def openSettings(self):
		""" Open or bring to front user settings dialog.
		"""
		if self.settings_dialog.isVisible():
			self.settings_dialog.activateWindow()
		else:
			self.settings_dialog.exec_()

		self.main_widget.view_main.toggleHorizontalScrollBar(settings.getWordWrap())
		self.main_widget.model_main.select()

	def toggleWindow(self):
		""" Hides or shows the main window based on user actions. Hides window 
			when user attempts to exit it with Alt+F4, CTRL+Q, or global hot 
			key. Shows window at user's cursor while checking to make sure it 
			does not go offscreen.
		"""
		# Store window position and size
		settings.setWindowPos(self.pos())
		settings.setWindowSize(self.size())

		if self.isVisible():
			self.hide()
		elif settings.getOpenWindowAt() == 1: 	# Last position
			self.move(settings.getWindowPos())
			self.resize(settings.getWindowSize())
			self.show()
			self.activateWindow()
		else: # settings.getOpenWindowAt() == 0 # At mouse cursor
			# Window mouse coordinates
			x_cursor = QtGui.QCursor().pos().x()
			y_cursor = QtGui.QCursor().pos().y()
			logging.debug('CursorCoords=(%d,%d)' % (x_cursor, y_cursor))

			desktop = QtGui.QDesktopWidget()
			current_screen = desktop.screenNumber(QtGui.QCursor().pos())

			# Determine global coordinates by summing screen(s) coordinates
			x_max = 0
			y_max = 99999
			for screen in range(0, desktop.screenCount()):
				x_max += desktop.availableGeometry(screen).width()
				
				y_screen = desktop.availableGeometry(screen).height()
				if y_screen < y_max:
					 y_max = y_screen

			x_min, y_min, _, _ = desktop.availableGeometry().getCoords()

			logging.debug('GlobalScreenRect=(%d,%d,%d,%d)' % (x_min, y_min, x_max
				, y_max))

			# Check if window will be offscreen based on mouse position and 
			# global screen coordinates
			if x_cursor < x_min:
				x = x_min
			elif x_cursor + self.size().width() > x_max:
				x = x_max - self.size().width()
			else:
				x = x_cursor

			if y_cursor < y_min:
				y = y_min
			elif y_cursor + self.size().height() > y_max:
				y = y_max - self.size().height()
			else:
				y = y_cursor

			logging.debug('WindowCoords=(%d,%d)' % (x, y))
			self.setGeometry(x, y, self.size().width(), self.size().height())

			# Clear search box from last interaction
			if len(self.main_widget.search_box.text()) != 0:
				self.main_widget.search_box.clear()

			self.show()
			self.activateWindow()

	def iconActivated(self, reason):
		"""	Toggle clipoard manager if system tray icon clicked
		"""	
		if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick):
			if self.isVisible():
				self.activateWindow()
			else:
				self.toggleWindow()

	def closeEvent(self, event):
		""" Hide window instead of exiting. Only method to quit is from
			System Tray context menu.
		"""
		event.ignore()
		self.hide()


class MainWidget(QtGui.QWidget):

	def __init__(self, parent):        
		super(MainWidget, self).__init__(parent)
		self.parent = parent

		# Ignore clipboard change when user sets item to clipboard
		self.ignore_created = False

		# Monitor clipboards
		self.clipboards = clipboards.Clipboards(self)

		# Create view, model, and proxy
		self.view_main = history.ListView(self)
		self.model_main = database.MainSqlTableModel(self)
		
		self.proxy_main = QtGui.QSortFilterProxyModel(self)
		self.proxy_main.setFilterKeyColumn(config.TITLE)
		self.proxy_main.setSourceModel(self.model_main)
		self.proxy_main.setDynamicSortFilter(True)
		self.proxy_main.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

		self.view_main.setModel(self.proxy_main)
		self.view_main.setModelColumn(config.TITLE)
		
		self.search_box = SearchBox(self.view_main, self.proxy_main)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.search_box)
		layout.addWidget(self.view_main)
		self.setLayout(layout)

		# Connect signals
		self.connect(self.clipboards, QtCore.SIGNAL('new-item(QObject)')
			, self.onNewItem)
		self.connect(self.search_box, QtCore.SIGNAL('textChanged(QString)')
			, self.proxy_main.setFilterFixedString)
		self.connect(self.search_box, QtCore.SIGNAL('returnPressed()')
			, self.onSetClipboard)
		self.connect(self.view_main, QtCore.SIGNAL('set-clipboard()')
			, self.onSetClipboard)

	def onNewItem(self, mime_data):
		"""	TODO: Support images and file copies
		"""

		# Do not perform the new item process because user just set clipboard contents
		if self.ignore_created:
			self.ignore_created = False
			return None

		logging.debug('Clipboard Formats: %s' % str(mime_data.formats()))

		# Determine what should the checksum should be calculated from
		checksum_string = None
		if mime_data.hasText():
			checksum_string = mime_data.text()
		if mime_data.hasHtml():
			checksum_string = mime_data.html()
		if mime_data.hasImage():
			checksum_string = str(QtCore.QByteArray(mime_data.data('application/x-qt-image')).toBase64())
		
		if not checksum_string:
			logging.warn('Mime Data does not have html, text, or image!')
			return None

		# CRASH FIX: Handle unicode characters for calculating checksum
		codec = QtCore.QTextCodec.codecForName('UTF-8')
		encoder = QtCore.QTextEncoder(codec)
		bytes = encoder.fromUnicode(checksum_string)	# QByteArray

		# Calculate checksum from bytes
		checksum = zlib.crc32(bytes)
		logging.debug('Checksum=%s' % checksum)

		# If duplicate then return, else insert new item
		if self.checkForDuplicate(checksum):
			return None

		# Convert mime data based on format to ByteArray
		data_insert = []
		for format in config._mimeReferences:

			if mime_data.hasFormat(format):
				byte_data = QtCore.QByteArray(mime_data.data(format))
				data_insert.append([format, byte_data])

		logging.debug(mime_data.text())
		for format, _ in data_insert:
			logging.debug('Format Saved: %s' % format)

		# Returns int(rowid) or None if failed
		parentid = database.insertMain(QtCore.QDateTime.currentMSecsSinceEpoch(), 
									   mime_data.text(), 
									   checksum)
		self.model_main.select()	# Update model and view

		# Store mime data into database
		logging.debug(parentid)
		if not parentid:
			logging.warn('ParentID=%s is missing Children!' % parentid)
			return None

		for format, byte_data in data_insert:
			database.insertMimeData(parentid, format, byte_data)

		# Highlight top item
		index = QtCore.QModelIndex(self.view_main.model().index(0, config.TITLE))
		self.view_main.setCurrentIndex(index)

		return None

	def checkForDuplicate(self, checksum):
		"""	Checks source model for a duplicate checksum on new item that
			requested to be created. If duplicate is found then update
			the source DATE column and submit changes. 
			
			Parameters
			----------
			checksum : str
				Calculated by zlib.crc32()

			Returns
			-------
			True/false : bool
				Duplicate found or not found
		"""
		# TODO: Investigate if SQL query is quicker on larger databases.
		for row in range(self.model_main.rowCount()):

			# Get CHECKSUM column from source's row
			source_index = self.model_main.index(row, config.CHECKSUM)
			checksum_source = self.model_main.data(source_index)

			# Update DATE column if checksums match
			if str(checksum) == str(checksum_source):
				logging.debug('%s == %s' % (checksum, checksum_source))
				
				self.model_main.setData(self.model_main.index(row, config.DATE)
					, QtCore.QDateTime.currentMSecsSinceEpoch())
				self.model_main.submit()
				
				return True

		return False

	def onSetClipboard(self):
		""" Passes QMimeData() to be set by clipboard by double click,
			press return, or through context menu action. The index of
			the selected item is determined from the proxy and mapped to the 
			source. The index PARENTID is determined from the source. There is
			a parent and child relationship in the Data DB. Each row that has
			the PARENTID is returned and the clipboard format and data are 
			written to QMimeData(). Finally, QMimeData is passed to the 
			clipboards module.
		"""
		self.ignore_created = True

		# Map the view->proxy to the source->db index
		proxy_index = self.view_main.currentIndex()
		source_index = self.proxy_main.mapToSource(proxy_index)
		
		# Get parent ID by creating a new index for data
		model_index = self.model_main.index(source_index.row(), config.ID)
		parentid = self.model_main.data(model_index)
		logging.debug('ParentID=%s' % parentid)

		# Update the date column in source
		self.model_main.setData(self.model_main.index(model_index.row(), config.DATE)
			, QtCore.QDateTime.currentMSecsSinceEpoch())
		self.model_main.submit()

		# Find all childs relating to parentid
		mime_list = database.getMatchingData(parentid)

		# Create QMimeData object based on formats and byte data
		mime_data = QtCore.QMimeData()
		for format, byte_data in mime_list:
			mime_data.setData(format, byte_data)
		
		# Set to clipboard
		self.clipboards.setData(mime_data)

		# Hide parent window
		self.window().hide()


if __name__ == '__main__':
	logging.debug('System=%s' % platform.system())

	app = ClipboardApp(sys.argv)

	# SQL driver fails to load if not in C:\Python27\sqldrivers
	app.addLibraryPath(os.path.join(QtCore.QDir.currentPath(), '/plugins'))

	logging.debug('SystemTheme=%s' % app.desktopSettingsAware())

	app.setOrganizationName(config.APP_ORG)
	app.setOrganizationDomain(config.APP_DOMAIN)
	app.setApplicationName(config.APP_NAME)

	app.singleStart()
	run = app.exec_()
	
	sys.exit(run)