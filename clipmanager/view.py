#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

from PySide import QtCore
from PySide import QtGui

from database import delete_mime
from defs import ID
from defs import TITLESHORT
from settings import settings

logging.getLogger(__name__)


class ListView(QtGui.QListView):
    """Clipboard history list.

    Todo:
        Investigate if storing QMimeData for each list item instead of doing
        a lookup in the database and creating it.
    """
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)
        self.parent = parent

        # Settings/design
        self.setLayoutMode(QtGui.QListView.SinglePass)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setAlternatingRowColors(True)
        self.setViewMode(QtGui.QListView.ListMode)
        self.setResizeMode(QtGui.QListView.Adjust)
        self.setStyleSheet('QListView::item {padding:10px;}')

        # Toggle horizontal scroll bar on and off if word wrap enabled
        self.set_horiz_scrollbar(settings.get_word_wrap())
        
        # Set view delegate
        delegate = ItemDelegate(self)
        self.setItemDelegate(delegate)

        # List item right click menu
        self._create_context_menu()

        # Item double clicked is set to clipboard
        self.doubleClicked.connect(self._emit_set_clipboard)

    def resizeEvent(self, event):
        """Reset view when user changes lines to display or word wrap settings.

        Args:
            event: QtGui.QResizeEvent

        Returns:
            Allow QListView.resizeEvent() to process.

        """
        self.emit(QtCore.SIGNAL('layoutChanged()'))
        self.reset()
        return QtGui.QListView.resizeEvent(self, event)

    def set_horiz_scrollbar(self, toggle):
        """Toggle horizontal scroll bar on and off.

        Args:
            toggle (int/bool): Turn on or off.
        """
        if toggle:
            scroll_bar = QtCore.Qt.ScrollBarAlwaysOff
        else:
            scroll_bar = QtCore.Qt.ScrollBarAsNeeded

        self.setHorizontalScrollBarPolicy(scroll_bar)

    def _exit(self):
        """Tell the application to exit with return code 0 (success).
        """
        QtCore.QCoreApplication.quit()

    def _create_context_menu(self):
        """Create right click menu item for items in list.
        """
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # Set item to clipboard
        apply_act = QtGui.QAction(QtGui.QIcon.fromTheme('list-add', 
                                  QtGui.QIcon('icons/add.png')), 
                                  'Set to clipboard', self)
        apply_act.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return))

        # Preview item's contents
        preview_act = QtGui.QAction(QtGui.QIcon.fromTheme('document', 
                                    QtGui.QIcon('icons/document.png')), 
                                    'Preview', self)
        preview_act.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F11))

        # Delete item
        delete_act = QtGui.QAction(QtGui.QIcon.fromTheme('list-remove', 
                                   QtGui.QIcon('icons/remove.png')),
                                   'Delete', self)
        delete_act.setShortcut(QtGui.QKeySequence.Delete)

        seperator_1 = QtGui.QAction(self)
        seperator_1.setSeparator(True)

        # Open settings dialog
        settings_act = QtGui.QAction(QtGui.QIcon.fromTheme('emblem-system', 
                                     QtGui.QIcon('icons/settings.png')),
                                     'Settings', self)

        seperator_2 = QtGui.QAction(self)
        seperator_2.setSeparator(True)

        # Exit
        exit_act = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit', 
                                 QtGui.QIcon('icons/exit.png')), 'Quit', self)

        self.addAction(apply_act)
        self.addAction(preview_act)
        self.addAction(delete_act)
        self.addAction(seperator_2)
        self.addAction(settings_act)
        self.addAction(seperator_1)
        self.addAction(exit_act)

        self.connect(apply_act, QtCore.SIGNAL('triggered()'), 
                     self._emit_set_clipboard)
        self.connect(preview_act, QtCore.SIGNAL('triggered()'), 
                     self._emit_open_preview)
        self.connect(delete_act, QtCore.SIGNAL('triggered()'),
                     self._delete_rows)
        self.connect(settings_act, QtCore.SIGNAL('triggered()'), 
                     self._emit_open_settings)
        self.connect(exit_act, QtCore.SIGNAL('triggered()'), self._exit)

    def keyPressEvent(self, event):
        """Set focus to search box if user starts typing text.

        Args: 
            event: QtCore.QEvent

        Returns:
            Allow QListView.keyPressEvent() to process.
        """
        # Catch select all <CTRL><A> on list
        if (event.modifiers() == QtCore.Qt.ControlModifier) and \
           (event.key() == QtCore.Qt.Key_A):
            return QtGui.QListView.keyPressEvent(self, event)

        # Scroll list view to the right (word wrap disabled)
        elif event.key() == QtCore.Qt.Key_Right:
            value = self.horizontalScrollBar().value()
            self.horizontalScrollBar().setValue(value+10)

        # Scroll list view to the left (word wrap disabled)
        elif event.key() == QtCore.Qt.Key_Left:
            value = self.horizontalScrollBar().value()
            self.horizontalScrollBar().setValue(value-10)

        # Give focus to search box if user starts typing letters
        elif event.text():
            self.parent.search_box.setText(self.parent.search_box.text() \
                 + event.text())
            self.parent.search_box.setFocus(QtCore.Qt.ActiveWindowFocusReason)
        
        return QtGui.QListView.keyPressEvent(self, event)

    @QtCore.Slot()
    def _emit_open_preview(self):
        """Emit signal with selected item's QModelIndex to open preview dialog.
        """
        self.emit(QtCore.SIGNAL('open-preview(QModelIndex)'),
                  self.currentIndex())

    @QtCore.Slot()
    def _emit_open_settings(self):
        """Emit signal to open settings dialog.
        """
        self.emit(QtCore.SIGNAL('open-settings()'))

    @QtCore.Slot()
    def _emit_set_clipboard(self):
        """Emit signal to set clipboard contents.

        Todo:
            Send list of selected indexes instead of just emitting a signal
            and having main window grab the selection.
        """
        # indexes = self.selectionModel().selectedIndexes() # QItemSelectionModel
        # for __ in indexes:
        self.emit(QtCore.SIGNAL('set-clipboard()'))

    @QtCore.Slot()
    def _delete_rows(self):
        """Delete selected indexes.

        CTRL+A on list view selects hidden columns. So even if user deselects 
        an item, it will still be deleted since the hidden column is still 
        selected. selectedRows(column=TITLE) wasn't working for QListView.
        """
        self.setCursor(QtCore.Qt.BusyCursor)

        selection_model = self.selectionModel()
        indexes = selection_model.selectedIndexes()
        logging.debug('Items selected: %d' % len(indexes))

        def get_row_id(index):
            """Sort by row number
            """
            return index.row()

        # Sort indexes by row number and delete each row and child mime data
        for index in sorted(indexes, key=get_row_id, reverse=True):
            if index.column() == TITLESHORT:
                row = index.row()
                logging.debug('ID: %d' % row)

                # Get model index
                model_index = self.model().index(row, ID)
                parent_id = self.model().data(model_index)
                
                delete_mime(parent_id)
                self.model().removeRow(row)
            else:
                pass

        self.unsetCursor()


class ItemDelegate(QtGui.QStyledItemDelegate):
    """Subclass paintnig and style of QListView items.
    """
    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)
        self.parent = parent
    
    def paint(self, painter, option, index):
        """Subclass of paint function.

        Args:
            painter: QtGui.QPainter
            option: QtGui.QStyleOptionViewItem
            index: QtCore.QModelIndex

        Returns:
            QtGui.QStyledItemDelegate.paint() if QModelIndex is not valid.

        References:
            http://pydoc.net/Python/gayeogi/0.6/gayeogi.plugins.player/
            https://github.com/fluggo/Canvas/blob/master/fluggo/editor/ui/plugineditor.py
        """
        if not index.isValid():
            return QtGui.QStyledItemDelegate.paint(self, painter, option, index)

        painter.save()

        # Draw selection highlight
        if option.state & QtGui.QStyle.State_Selected:
            painter.setPen(QtGui.QPen(option.palette.highlightedText(), 0))
            painter.fillRect(option.rect, option.palette.highlight())

        # if index.data() == 'application/x-qt-image':
        #     parent_index = QtCore.QModelIndex(self.model().index(0, ID))
        #     print parent_index.column()

        # Set alignment and enable word wrap if applicable
        text_option = QtGui.QTextOption()
        text_option.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        # if settings.get_word_wrap():
        #     text_option.setWrapMode(QtGui.QTextOption.WrapAnywhere)

        # Add padding to left and right side of text
        text_rect = option.rect
        text_rect.setLeft(text_rect.left() + 5)
        text_rect.setRight(text_rect.right() - 5)

        painter.drawText(text_rect, index.data(), o=text_option)
        painter.restore()

    def sizeHint(self, option, index):
        """Option size is calculated by creating a QTextDocument with modified
        text and determining the dimensions.

        Args:
            option: QtGui.QStyleOptionViewItem
            index: QtCore.QModelIndex

        Returns:
            QtGui.QStyledItemDelegate.sizeHint() if QModelIndex is invalid.

        References:
            http://qt-project.org/forums/viewthread/12186

        Todo:
            Look into using font metrics bounding rect.
            Handle lines to display in relation to word wrap.
        """
        if not index.isValid():
            return QtGui.QStyledItemDelegate.sizeHint(self, option, index)

        doc = QtGui.QTextDocument() # Inserting self creates a memory leak!

        # Set alignment and enable word wrap if applicable
        text_option = QtGui.QTextOption()
        text_option.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        # Reimplement as lines to display can be ignored if word wrap forces
        # an extra line to be created
        # if settings.get_word_wrap():
        #     text_option.setWrapMode(QtGui.QTextOption.WrapAnywhere)
            
        doc.setDefaultTextOption(text_option)
        doc.setPlainText(index.data())

        # Add some padding to each item, + 10
        return QtCore.QSize(doc.size().width(), doc.size().height() + 5)
        
    # def sizeHint(self, option, index):
    #     if not index.isValid():
    #         return QtGui.QStyledItemDelegate.sizeHint(self, option, index)

    #     fake_text = 'Line1\nLine2\nLine3\n'
    #     fake_fm = option.fontMetrics
    #     fake_font_rect = fake_fm.boundingRect(option.rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop|QtCore.Qt.TextWordWrap, fake_text)

    #     real_text = index.data()
    #     real_fm = option.fontMetrics
    #     real_font_rect = real_fm.boundingRect(option.rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop|QtCore.Qt.TextWordWrap, real_text)

    #     if real_font_rect.height() < fake_font_rect.height():
    #         height = real_font_rect.height()
    #     else:
    #         height = fake_font_rect.height()

    #     return QtCore.QSize(real_font_rect.width(), height+10)

    # def flags(self, index):
    #     """Sublass of flags method.

    #     Args:
    #         index: QtCore.QModelIndex
    #     """
    #     if not index.isValid():
    #         return QtCore.Qt.ItemFlags()
        
    #     return QtCore.Qt.ItemFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)