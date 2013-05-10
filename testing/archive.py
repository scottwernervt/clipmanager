def dictFactory(cursor, row):
	""" http://stackoverflow.com/questions/811548/sqlite-and-python-return-a-dictionary-using-fetchone
	"""
	d = {}
	for idx,col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d


class Contents(QListView):
	
	def __init__(self, parent=None):
		super(Contents, self).__init__(parent)
		self.setWordWrap(False)
		self.setFlow(QListView.TopToBottom)
		self.setAcceptDrops(False)
		self.setDragEnabled(False)
		self.setSpacing(0)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setAlternatingRowColors(True)

		self.keyPressEvent = self.keyPressEvent
		self.connect(self, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.moveToTop)

	def moveToTop(self, item):
		# Widget is on top row so do not move, just set clipboard contents
		current_row = self.row(item)
		logging.debug('current_row: %s' % current_row)
		if current_row == 0:
			self.emit(SIGNAL('set-clipboard(int)'), None)
			return None
		
		selectedItem = self.currentItem()
		selectedWidget = self.itemWidget(selectedItem)

		rowid = selectedWidget.rowid
		date = selectedWidget.date
		title = selectedWidget.title
		checksum = selectedWidget.checksum
		mime_data = selectedWidget.mime_data

		self.add(rowid, date, title, checksum, mime_data)

		# item = self.takeItem(current_row)
		# self.update()
		# self.add()
		# selectedItem = self.currentItem()
		# selectedWidget = self.itemWidget(selectedItem)
		# print 'Saved as new objects:'
		# print 'selectedItem',selectedItem,id(selectedItem),dir(selectedItem)
		# print 'selectedWidget',selectedWidget,id(selectedWidget),dir(selectedWidget)

		# self.removeItemWidget(selectedItem)
		# item = self.takeItem(current_row)
		# del item
		# print 'Removing selected objects'
		# print 'selectedItem',selectedItem,id(selectedItem),dir(selectedItem)
		# print 'selectedWidget',selectedWidget,id(selectedWidget),dir(selectedWidget)

		# self.add(selectedWidget)

		# # Remove item from list and destroy widget
		# itemSelected = self.takeItem(current_row)
		# self.removeItemWidget(itemSelected)
		# del itemSelected
		# print id(temp)

		
		# Set clipboard contents
		self.emit(SIGNAL('set-clipboard(int)'), rowid)

		# current_row = self.row(item)
		# rowid = self.itemWidget(item).rowid

		# # Widget is on top row so do not move, just set clipboard contents
		# logging.debug('current_row: %s' % current_row)
		# if current_row == 0:
		# 	self.emit(SIGNAL('set-clipboard(int)'), None)
		# 	return None

		# print 'I am running'
		# # Remove item from list and destroy widget
		# itemSelected = self.takeItem(current_row)
		# self.removeItemWidget(itemSelected)
		# itemSelected = None

		# # Set clipboard contents
		# self.emit(SIGNAL('set-clipboard(int)'), rowid)

	def add(self, rowid, date, title, checksum, mime_data):
		# Create widget used for displaying in list
		widget = ListItem(rowid, date, title, checksum)
		widget.addMimeData(mime_data)
		widget.setDisplay()
		
		# Create item container for widget above
		newItem = QListWidgetItem()
		newItem.setSizeHint(QSize(0, _itemHeight))

		self.insertItem(0, newItem)
		self.setItemWidget(newItem, widget)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Return:
			self.moveToTop(self.currentItem())
		elif event.key() == Qt.Key_Up:
			if self.currentRow() is not 0:
				self.setCurrentRow(self.currentRow()-1)
		elif event.key() == Qt.Key_Down:
			if self.currentRow() < self.count()-1:
				self.setCurrentRow(self.currentRow()+1)

class ListItem(QWidget):

	def __init__(self, rowid, date, title, checksum, parent=None):
		super(ListItem, self).__init__(parent)
		# Store information from database
		self.rowid = rowid
		self.date = date
		self.title = title
		self.checksum = checksum

		# self.settyleSheet('QToolTip {white-space:pre}')

		self.mime_data = QMimeData()

		# TODO: Rename left and right lbl
		self.leftLbl = QLabel()
		self.leftLbl.setAlignment(Qt.AlignLeft)
		self.leftLbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.leftLbl.setScaledContents(False)	# If true, will fill label ignoring aspect of images
		self.leftLbl.setWordWrap(True)

		# self.rightLbl = QLabel()
		# self.rightLbl.setAlignment(Qt.AlignLeft)
		# self.rightLbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		# self.rightLbl.setWordWrap(True)

		layout = QHBoxLayout()
		layout.addWidget(self.leftLbl)
		# layout.addWidget(self.rightLbl)
		self.setLayout(layout)

	def MimeData(self, db_data):
		"""Store multiple formats/data into QMimeData() object to be used by clipboard."""
		for (_, _, format, data) in db_data:
			self.mime_data.setData(format, str(data))

	def setDisplay(self):
		"""Check type of QMimeDate is present and displays it accordingly.
		Image: Thumbnnail in list and on tooltip (physical file made)
		Html/Plain: Display rich text in list and tooltip."""

		time_human = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(self.date))
		
		# If QMimeData() has an image then display a thumbnail in list/tooltip and text if came
		# from a filename
		if self.mime_data.hasImage():
			byte_array = self.mime_data.imageData()
			# .scaled(): Return type of this function is QPixmap, so it returns a scaled copy of the original pixmap.
			pixmap = QPixmap()
			pixmap.loadFromData(byte_array)
			scaled = pixmap.scaledToHeight(_itemHeight, mode=Qt.FastTransformation)
			
			# Save image to hard disk for tooltip
			image_path = os.path.join(_pwd, 'images/', '%s.png' % str(self.rowid))
			pixmap.save(image_path, format='PNG', quality=-1)

			text = ''
			tooltip_header = '<img src="%s"></img>' % image_path
			tooltip_footer = '<br><br><i>Saved:</i> %s' % time_human
			
			self.setToolTip(tooltip_header + tooltip_footer)
			self.leftLbl.setPixmap(scaled)

		elif self.mime_data.hasHtml():
			text = self.mime_data.html()
			tooltip_header = text.rstrip(' \t\r\n\0').lstrip(' \t\r\n\0')
			tooltip_footer = '<br><br><i>Saved:</i> %s' % time_human

			self.setToolTip(tooltip_header + tooltip_footer)
			self.leftLbl.setText(text)

		elif self.mime_data.hasText():
			text = self.mime_data.text()
			text = textwrap.dedent(text).replace('\t', '  ').rstrip().lstrip()
			tooltip_header = text
			tooltip_footer = '\n\nSaved: %s' % time_human

			self.setToolTip(tooltip_header + tooltip_footer)
			self.leftLbl.setText(text)

		else:
			print 'Ahhhh shit we fucked up.'


		# formatted = textwrap.dedent(tooltip_header).replace('\t', '  ').rstrip().lstrip()
		# tooltip_footer = 'Created: %s' % time.strftime("%a, %d %b %Y %H:%M:%S", 
		# 	time.localtime(self.date))
		
		# tooltip = '%s\n\n%s' % (formatted, tooltip_footer)
		# print tooltip
		# self.setToolTip(tooltip)

		# self.setToolTip(text)
		# formatted = textwrap.dedent(self.data).replace('\t', '  ').rstrip().lstrip()
		# time_human = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(self.created))
		# tooltip = '%s\n\nCreated: %s' % (formatted, time_human)
		# self.setToolTip(tooltip)

		# font = QFont()
		# font.setPointSize(8)

		# self.text = QLabel()
		# self.text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		# self.text.setFont(font)
		# self.text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		# self.text.setWordWrap(True)		
		# self.text.setText(formatted)

		# # Determine what icon type to show
		# self.icon = QLabel()
		# self.icon.setFont(font)
		# if 'html' in self.mime_type:
		# 	icon_label = 'html'
		# else:
		# 	icon_label = 'plain'

		# # pixmap = QPixmap(os.path.join(self.path, 'icons/txt.gif'))
		# # pixmap.scaled(28, 28, aspectMode=Qt.KeepAspectRatio, mode=Qt.FastTransformation)
		# # self.icon.setScaledContents(True)
		# # self.icon.setPixmap(pixmap)
		
		# self.icon.setText(icon_label)

		# layout = QHBoxLayout()
		# layout.addWidget(self.icon)
		# layout.addWidget(self.text)
		# self.setLayout(layout)

class ListModel(QAbstractListModel):
	# Model: data stored
	# View: display model data
	def __init__(self, contents, parent=None):
		super(ListModel, self).__init__(parent)
		self._contents = contents

	def columnCount(self):
		return 1

	def rowCount(self, parent):
		""" Required, tells the view how many items it contains.
		"""
		return len(self._contents)

	def data(self, index, role):
		""" Required, returns the item of data that coressponds to 
			the index parameter given.

			index: QModelIndex class: row(), column(), parent(), etc
			role: returns different types of data like decorations
		"""
		row = index.row()

		if not index.isValid():
			return QVariant()

		if role == Qt.DisplayRole:
			return self._contents[row]
			# return QVariant(self._contents[index.row()]['title'])

		if role == Qt.ToolTipRole:
			return self._contents[row]['date']

		return


		# Qt.DisplayRole Text of the item   (QString)
		# Qt.DecorationRole Icon of the item   (QColor, QIcon or QPixmap)
		# Qt.EditRole Editing data for editor   (QString)
		# Qt.ToolTipRole Tooltip of the item   (QString)
		# Qt.StatusTipRole Text in the status bar   (QString)
		# Qt.WhatsThisRole Text in "What's This?" mode   (QString)
		# Qt.SizeHintRole Size hint in view   (QSize)


		# if role == Qt.EditRole:
		# 	# Keeps original value of entry when editing
		# 	return self._contents[index.row()]



		# if role == Qt.DecorationRole:
		# 	row = index.row()
		# 	value = self._contents[row]

		# 	pixmap = QPixmap(26,26)
		# 	pixmap.fill('000000')

		# 	icon = QIcon(pixmap)
		# 	return icon

		# if role == Qt.DisplayRole:
		# 	row = index.row()
		# 	value = self._contents[row]['title']

		# 	return value

		# if role == Qt.BackgroundRole:
		# 	if index.row() % 2 == 0:
		# 		return QColor(Qt.gray)
		# 	else:
		# 		return QColor(Qt.lightGray)

		# return

	def setData(self, index, value, role=Qt.EditRole):
		""" 
			index: contains row/column/parent of item
			value: value typed while editing item
		"""
		return

	def insertData(self, data):
		self.beginResetModel()
		self._contents.insert(0, data)
		self.endResetModel()

	# def insertRows(self, position, rows, parent=QModelIndex()):
	# 	"""
	# 		position: where in the data structure we want to insert
	# 		rows: how many rows we want to insert
	# 		parent: for tree views 
	# 	"""
	# 	# Must call at start to keep views in sync
	# 	# rows is a count
	# 	self.beginInsertRows(parent, position, position + rows - 1)

	# 	for i in range(rows):
	# 		self._contents.insert(position, 'Insert Test')

	# 	# Must call at end to keep views in sync
	# 	self.endInsertRows()

	# def removeRows(self, position, rows, parent=QModelIndex()):
	# 	"""
	# 		position: where in the data structure we want to remove
	# 		rows: how many rows we want to remove
	# 		parent: for tree views 
	# 	"""
	# 	# Must call at start to keep views in sync
	# 	# rows is a count
	# 	self.beginInsertRows(parent, position, position + rows - 1)

	# 	for i in range(rows):
	# 		value = self._contents[position]
	# 		self._contents.remove(value)

	# 	# Must call at end to keep views in sync
	# 	self.endInsertRows()

	# 	return True

	def flags(self, index):
		"""	Called by the view to check the state of the items. Flags 
			function overides default from QAbstractListModel. How
			should we treat the items?
		"""
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable

class Db(object):

	def __init__(self, parent=None):
		self._table = 'main'
		self.conn = sqlite3.connect('Contents.db')
		self.conn.row_factory = dictFactory
		self.cursor = self.conn.cursor()

	def connect(self):
		return sqlite3.connect('contents.db')

	def close(self):
		"""Close connection to database"""
		self.conn.close()

	def createTable(self):
		"""Create table in database"""
		for table in (_tblMain, _tblData):
			try:
				self.cursor.execute(table)
			except sqlite3.OperationalError as err:
				logging.debug(err)
				
		self.conn.commit()

	def findDuplicate(self, checksum):
		self.cursor.execute('SELECT id FROM Main WHERE checksum = ?',  (checksum,))
		rowid = self.cursor.fetchone()
		return rowid

	def updateTime(self, rowid, date):
		self.cursor.execute('UPDATE Main SET date = %d WHERE id = ?' % date
			, (rowid,))
		self.conn.commit()

	def deleteMain(self, rowid):
		self.cursor.execute('DELETE FROM Main where id = ?' % rowid)
		self.conn.commit()

	def addToMain(self, date, title, checksum):
		"""
		"""
		self.cursor.execute('INSERT OR FAIL INTO Main values (Null,?,?,?)'
			, (date, title, checksum))
		self.conn.commit()

		return self.cursor.lastrowid

	def addToData(self, parentid, format, data):
		self.cursor.execute('INSERT OR FAIL INTO Data values (Null,?,?,?)'
			, (parentid, format, sqlite3.Binary(data)))

		self.conn.commit()

	def addOld(self, mime_data):
		"""Add new clipboard item to database history. If matching
		checksum is found in database, we will just update the created
		time. Signal that history has new item or been updated.
		Returns tuple: (True/False, int(rowid))
			True: New item
			False: Duplicate"""
		# Build list of mime data storing the format and binary data
		# [['text/plain', 'hello world'], ...]
		data_insert = []
		for format in mime_data.formats():
			if format in _mimeReferences:
				byte_data = QByteArray(mime_data.data(format))
				data_insert.append([format, byte_data])
			else:
				pass

		# Checmsum based off source format:
		# [..., u'application/x-qt-windows-mime;value="SkypeMessageFragment"'
		checksum = zlib.crc32(data_insert[-1][1])
		date = time.time()

		# Check for duplicate with checksum
		# rowid = (id, )
		self.cursor.execute('SELECT id FROM Main WHERE checksum = ?',  (checksum,))
		rowid = self.cursor.fetchone()

		if rowid is None:
			title = mime_data.text()
			if title == '':
				title = data_insert[-1][0]

			# Insert into Main db
			self.cursor.execute('INSERT OR FAIL INTO Main values (Null,?,?,?)'
				, (date, title, checksum))
			rowid = self.cursor.lastrowid

			logging.debug(date)
			logging.debug(title)
			logging.debug(checksum)
			logging.debug(rowid)
			logging.debug(data_insert)

			# Insert format/data into Data db
			for format, data in data_insert:
				self.cursor.execute('INSERT OR FAIL INTO Data values (Null,?,?,?)'
					, (rowid, format, sqlite3.Binary(data)))

			self.conn.commit()

			logging.debug('New: %s' % str(rowid))
			return (False, rowid)
		else:
			# Set to integer, tuples giving me headaches
			logging.debug('Duplicate: %s' % rowid[0])
			self.updateTime(rowid)
			return (True, rowid[0])

		# Something went wrong if we made it to here
		logging.warn(str(rowid))
		return (False, rowid)
	
	def getAllChildren(self, rowid):
		"""Returns single row's data as a tupple"""
		self.cursor.execute('SELECT * FROM Data WHERE parentid = ?'
			, (rowid, ))
		return self.cursor.fetchall()

	def getMain(self, rowid):
		logging.debug(rowid)
		"""Returns single row's data as a tupple"""
		self.cursor.execute('SELECT * FROM Main WHERE id = ?'
			, (rowid,))
		return self.cursor.fetchone()

	def getAllParents(self):
		"""Return entire database in list format, [(col1,col2,...),()]
		sorted by the time it was created"""
		self.cursor.execute('SELECT * FROM Main ORDER BY date DESC')
		# self.cursor.execute('SELECT * FROM Main ORDER BY date ASC')
		return self.cursor.fetchall()
