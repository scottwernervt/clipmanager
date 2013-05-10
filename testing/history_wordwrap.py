#!/usr/bin/python
# -*- coding: utf-8 -*-
#coding=utf-8

import logging
logging.getLogger(__name__)

from settings import settings
from config import *
import database

import os
import textwrap

from PySide.QtCore import *
from PySide.QtGui import *


def removeExtraLines(text, num_of_lines):
	""" Truncate string of text to 3 lines for display.
		Parameters
			text : string

		Returns
			text : original string if less than 3 lines if not then 
			truncated.
	"""
	# Remove blank lines
	text = os.linesep.join([s for s in text.splitlines() if s]) 
	lines = text.split('\n')
	if len(lines) > num_of_lines:
		text = '\n'.join(lines[:num_of_lines])

	return text


class ListView(QListView):
	"""	TODO:
		- Add right click menu
	"""
	def __init__(self, parent=None):
		super(ListView, self).__init__(parent)
		self.parent = parent

		self.setLayoutMode(QListView.SinglePass)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setDragEnabled(False)
		self.setAcceptDrops(False)
		self.setAlternatingRowColors(True)
		self.setViewMode(QListView.ListMode)
		self.setWrap()
		
		stylesheet = 'QListView::item {padding:5px;}'
		self.setStyleSheet(stylesheet)

		self.createContextMenu()

		self.connect(self.deleteAction, SIGNAL('triggered()'), self.deleteItem)
		self.connect(self.setAction, SIGNAL('triggered()'), self.emitSetClipboard)
		self.connect(self.settingsAction, SIGNAL('triggered()'), self.parent.parent.openSettings)
		self.doubleClicked.connect(self.emitSetClipboard)

	def setWrap(self):
		if settings.getWordWrap():
			wrap = True
			scroll_bar = Qt.ScrollBarAlwaysOff
		else:
			wrap = False
			scroll_bar = Qt.ScrollBarAsNeeded

		self.setWordWrap(wrap)
		self.setHorizontalScrollBarPolicy(scroll_bar)

	def createContextMenu(self):
		# Create context menu for list
		self.setContextMenuPolicy(Qt.ActionsContextMenu)

		self.deleteAction = QAction(QIcon.fromTheme('list-remove'), 'Delete', self)
		self.deleteAction.setShortcut(QKeySequence.Delete)

		self.setAction = QAction(QIcon.fromTheme('list-add'), 'Set to clipboard', self)
		self.setAction.setShortcut(QKeySequence(Qt.Key_Return))

		self.seperator = QAction(self)
		self.seperator.setSeparator(True)

		self.settingsAction = QAction(QIcon.fromTheme('emblem-system'), 'Settings', self)

		self.addAction(self.setAction)
		self.addAction(self.deleteAction)
		self.addAction(self.seperator)
		self.addAction(self.settingsAction)

	def keyPressEvent(self, event):
		""" Set focus to search box if user starts typing text when focus
			is on list view.
			obj : QListView
			event : QEvent
		"""
		if event.key() == Qt.Key_Right:
			value = self.horizontalScrollBar().value()
			self.horizontalScrollBar().setValue(value+10)
		elif event.key() == Qt.Key_Left:
			value = self.horizontalScrollBar().value()
			self.horizontalScrollBar().setValue(value-10)
		elif event.text(): # (event.type() == QEvent.KeyPress) and 
			# Give focus to search box if user starts typing letters
			self.parent.search_box.setText(self.parent.search_box.text() \
				 + event.text())
			self.parent.search_box.setFocus(Qt.ActiveWindowFocusReason)
		else:
			# Allow events to process (like entering text)
			return QListView.keyPressEvent(self, event)

	def emitSetClipboard(self):
		"""	TODO: Handle setting multiple selections to clipboard. Possibly merge 
			text into one clipboard item?
		"""
		indexes = self.selectionModel().selectedIndexes()	# QItemSelectionModel
		for index in indexes:
			self.emit(SIGNAL('set-clipboard()'))

	def deleteItem(self):
		indexes = self.selectionModel().selectedIndexes()
		
		def byRow(item):
			# Get row # from QModelIndex()
			return item.row()

		# Delete rows from greatest to least
		for index in sorted(indexes, key=byRow, reverse=True):
			row = index.row()
			source_index = self.model().index(row, ID)
			parent_id = self.model().data(source_index, Qt.DisplayRole)

			logging.debug('ParentID=%s' % parent_id)
			self.model().removeRow(row)
			database.deleteMimeData(parent_id)


class ItemDelegate(QStyledItemDelegate):
	""" Helped http://qt-project.org/forums/viewthread/25195"""
	"""	Draws/renders the the item's contents
	http://www.mimec.org/node/337
	http://qt-articles.blogspot.com/2010/07/how-to-customize-listview-in-qt-using.html
	http://www.developer.nokia.com/Community/Discussion/showthread.php?213346-Adding-Custom-Widgets-to-QListView
	http://www.developer.nokia.com/Community/Discussion/showthread.php?217027-Display-widget-as-items-in-a-QListView
	http://www.qtcentre.org/threads/27777-Customize-QListWidgetItem-how-to
	http://www.qtcentre.org/threads/46580-QStyledItemDelegate-draw-an-items-with-a-different-size-text-and-heights
	http://www.developer.nokia.com/Community/Discussion/showthread.php?217027-Display-widget-as-items-in-a-QListView
	http://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt
	http://qt-project.org/forums/viewthread/25195

	"""
	def __init__(self, parent=None):
		super(ItemDelegate, self).__init__(parent)
		self.parent = parent

	def paint(self, painter, option, index):
		if not index.isValid():
			return None

		rect = QRect(option.rect.topLeft(), option.rect.bottomRight())
		if (option.state & QStyle.State_Selected):
			painter.fillRect(rect, option.palette.highlight())

		painter.save()
		# painter.setPen(QPen(Qt.gray))
		# painter.drawLine(rect.topLeft(), rect.topRight())
		painter.restore()

		# rect.setLeft(rect.left() + 5)
		# rect.setTop(rect.top() + 10)
		# rect.setRight(rect.right() - 5)

		title = removeExtraLines(unicode(index.data())
			, int(settings.getLinesToDisplay()))

		painter.drawText(rect, Qt.TextWordWrap, title)
		# painter.save()

	def sizeHint(self, option, index):
		font_metrics = option.fontMetrics
		
		text = unicode(index.model().data(index))
		text = removeExtraLines(text
			, int(settings.getLinesToDisplay()))
		words = text.split(' ')
		bounding_rect = font_metrics.boundingRect(text)

		width = option.rect.width()
		times = 0
		for word in words:
			times += 1
			line_width = 0

			while len(words) > 0:
				word = words[0]
				word_width = font_metrics.width(word)
				if word_width + line_width < width:
					line_width += word_width
					line_width += font_metrics.width(' ')
					words.pop(0)
				else:
					# View space has been filled so stop
					break

		return QSize(width, bounding_rect.height() * times - times + 1)


		# title = removeExtraLines(text
		# 	, int(settings.getLinesToDisplay()))

		# # Highlight selected items
		# if option.state & QStyle.State_Selected:
		# 	# If petPen is not set then text will be black when highlighted
		# 	# I think I am doing something wrmong with the subclassing
		# 	painter.setPen(option.palette.color(QPalette.HighlightedText))
		# 	painter.fillRect(option.rect, option.palette.highlight())

		# # QRect r = option.rect.adjusted(2, 2, -2, -2);
		# title_rect = option.rect
		# title_rect.setLeft(title_rect.left() + 5)
		# title_rect.setTop(title_rect.top() + 5)
		# title_rect.setRight(title_rect.right() - 5)
		# title_rect.setBottom(title_rect.bottom() - 5)

		# painter.drawText(title_rect, Qt.AlignVCenter | Qt.AlignLeft, title);
		# painter.setFont(messageFont)

		# painter.restore()

		# return True

	# def sizeHint(self, option, index):
	# 	"""
	# 	http://www.qtcentre.org/threads/7278-QListView-word-wrap
	# 	"""
	# 	model = index.model()
	# 	row = index.row()

	# 	text = model.data(model.index(row, TITLE))
	# 	title = removeExtraLines(text
	# 		, int(settings.getLinesToDisplay()))

	# 	doc = QTextDocument(self)
	# 	doc.setPlainText(title)
	# 	return QSize(doc.idealWidth(), doc.size().height()+15)
	# 	# return QSize(50, doc.size().height()+10)

	# 	# font = QFont("times", 24)
	# 	# fm = QFontMetrics(font)
	# 	# pixelsWide = fm.width("What's the width of this text?")
	# 	# pixelsHigh = fm.height()

	# 	# print pixelsHigh

	# def sizeHint(self, option, index):
	# 	model = index.model()
	# 	row = index.row()
	# 	text = model.data(model.index(row, TITLE))
	# 	title = removeExtraLines(text)

	# 	return option.fontMetrics.size(1, title)
		# return QSize(option.rect.width(), option.rect.height()*10)
		# # http://qt-project.org/forums/viewthread/25122
		# model = index.model()
		# row = index.row()

		# text = model.data(model.index(row, TITLE))
		# title = removeExtraLines(text)
		# r = option.rect
		# s = option.fontMetrics.boundingRect(r.left(), r.top(), r.width(), r.height(), Qt.AlignVCenter | Qt.AlignLeft, title).size()

		# return s
		# const QString text = index.data(Qt::DisplayRole).toString();
  #       QRect r = option.rect.adjusted(2, 2, -2, -2);
  #       QSize s = option.fontMetrics.boundingRect(r.left(), r.top(), r.width(), r.height(), Qt::AlignVCenter|Qt::AlignLeft|Qt::TextWordWrap, text).size();


	def flags(self, index):
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable
