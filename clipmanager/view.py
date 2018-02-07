import logging

from PySide.QtCore import QCoreApplication, QSize, Qt, SIGNAL, Slot
from PySide.QtGui import (
    QAbstractItemView,
    QAction,
    QIcon,
    QKeySequence,
    QListView,
    QMenu,
    QPen,
    QStyle,
    QStyledItemDelegate,
    QTextDocument,
    QTextOption,
)

from clipmanager.database import delete_mime
from clipmanager.defs import ID, TITLE_SHORT
from clipmanager.settings import settings
from clipmanager.utils import resource_filename

logger = logging.getLogger(__name__)


class HistoryListView(QListView):
    """Clipboard history list."""

    def __init__(self, parent=None):
        super(HistoryListView, self).__init__(parent)

        self.parent = parent

        self.setLayoutMode(QListView.SinglePass)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setAlternatingRowColors(True)
        self.setViewMode(QListView.ListMode)
        self.setResizeMode(QListView.Adjust)
        self.setStyleSheet('QListView::item {padding:10px;}')
        self.setItemDelegate(HistoryListItemDelegate(self))

        self.toggle_horizontal_scrollbar(settings.get_word_wrap())

        self._build_menu()
        self.addAction(self.apply_action)
        self.addAction(self.preview_action)
        self.addAction(self.delete_action)

        self.doubleClicked.connect(self._emit_set_clipboard)

    def resizeEvent(self, event):
        """Reset list view when word wrap setting changed.

        :param event:
        :type event: QResizeEvent

        :return:
        :rtype: QListView.resizeEvent()
        """
        self.emit(SIGNAL('layoutChanged()'))
        self.reset()
        return QListView.resizeEvent(self, event)

    def contextMenuEvent(self, event):
        """Capture context menu event.

        :param event:
        :type event: QEvent

        :return:
        :rtype:
        """
        # Get selected item
        # indexes = self.selectionModel().selectedIndexes()
        # self.apply_action.setChecked(True)

        # Open menu
        self.menu.exec_(self.mapToGlobal(event.pos()))

    def keyPressEvent(self, event):
        """Automatically set focus to search box when typing.

        :param event:
        :type event: QEvent

        :return:
        :rtype: QListView.keyPressEvent()
        """
        # Catch select all <CTRL><A> on list
        if (event.modifiers() == Qt.ControlModifier) and \
                (event.key() == Qt.Key_A):
            return QListView.keyPressEvent(self, event)

        # Scroll list view to the right (word wrap disabled)
        elif event.key() == Qt.Key_Right:
            value = self.horizontalScrollBar().value()
            self.horizontalScrollBar().setValue(value + 10)

        # Scroll list view to the left (word wrap disabled)
        elif event.key() == Qt.Key_Left:
            value = self.horizontalScrollBar().value()
            self.horizontalScrollBar().setValue(value - 10)

        # Give focus to search box if user starts typing letters
        elif event.text():
            self.parent.search_box.setText(self.parent.search_box.text() \
                                           + event.text())
            self.parent.search_box.setFocus(Qt.ActiveWindowFocusReason)

        return QListView.keyPressEvent(self, event)

    @Slot()
    def _emit_open_preview(self):
        """Send open preview signal with selection index.

        :return: None
        :rtype: None
        """
        self.emit(SIGNAL('openPreview(QModelIndex)'), self.currentIndex())

    @Slot()
    def _emit_open_settings(self):
        """Send open settings dialog signal.

        :return: None
        :rtype: None
        """
        self.emit(SIGNAL('openSettings()'))

    @Slot()
    def _emit_set_clipboard(self):
        """Send set clipboard signal.

        Todo:
        * Send list of selected indexes instead of just emitting a signal
        * and having main window grab the selection.

        :return: None
        :rtype: None
        """
        # indexes = self.selectionModel().selectedIndexes() # QItemSelectionModel
        # for __ in indexes:
        self.emit(SIGNAL('setClipboard()'))

    @Slot()
    def _delete_rows(self):
        """Delete selected rows.

        CTRL+A on list view selects hidden columns. So even if user deselects
        an item, it will still be deleted since the hidden column is still
        selected.

        :return: None
        :rtype: None
        """
        self.setCursor(Qt.BusyCursor)

        selection_model = self.selectionModel()
        indexes = selection_model.selectedIndexes()

        def get_row_id(idx):
            """Sort row by ids.

            :param idx:
            :type idx: QModelIndex

            :return: Row index.
            :rtype:int
            """
            return idx.row()

        # Sort indexes by row number and delete each row and child mime data
        for index in sorted(indexes, key=get_row_id, reverse=True):
            if index.column() == TITLE_SHORT:
                row = index.row()

                # Get model index
                model_index = self.model().index(row, ID)
                parent_id = self.model().data(model_index)

                delete_mime(parent_id)
                self.model().removeRow(row)
                self.model().sourceModel().submitAll()
            else:
                pass

        self.model().submit()
        self.unsetCursor()

    def _build_menu(self):
        """Create right click menu and actions."

        :return: None
        :rtype: None
        """
        self.menu = QMenu(self)

        # Set item to clipboard
        self.apply_action = QAction(
            QIcon.fromTheme(
                'list-add',
                QIcon(resource_filename('icons/add.png'))
            ),
            'Set to clipboard',
            self
        )
        self.apply_action.setShortcut(QKeySequence(Qt.Key_Return))

        # Preview item's contents
        self.preview_action = QAction(
            QIcon.fromTheme(
                'document',
                QIcon(resource_filename('icons/document.png'))
            ),
            'Preview',
            self
        )
        self.preview_action.setShortcut(QKeySequence(Qt.Key_F11))

        # Prevent item from being deleted
        self.save_action = QAction('Never delete', self)
        self.save_action.setCheckable(True)

        # Delete item
        self.delete_action = QAction(
            QIcon.fromTheme(
                'list-remove',
                QIcon(resource_filename('icons/remove.png'))
            ),
            'Delete',
            self
        )
        self.delete_action.setShortcut(QKeySequence.Delete)

        separator_1 = QAction(self)
        separator_1.setSeparator(True)

        # Open settings dialog
        settings_act = QAction(
            QIcon.fromTheme(
                'emblem-system',
                QIcon(resource_filename('icons/settings.png'))
            ),
            'Settings',
            self
        )

        separator_2 = QAction(self)
        separator_2.setSeparator(True)

        # Exit
        exit_action = QAction(
            QIcon.fromTheme(
                'application-exit',
                QIcon(resource_filename('icons/exit.png'))
            ),
            'Quit',
            self
        )

        # Add to menu
        self.menu.addAction(self.apply_action)
        self.menu.addAction(self.preview_action)
        self.menu.addAction(self.save_action)
        self.menu.addAction(self.delete_action)
        self.menu.addAction(separator_2)
        self.menu.addAction(settings_act)
        self.menu.addAction(separator_1)
        self.menu.addAction(exit_action)

        # Connect signal for each action
        self.menu.connect(self.apply_action,
                          SIGNAL('triggered()'),
                          self._emit_set_clipboard)
        self.menu.connect(self.preview_action,
                          SIGNAL('triggered()'),
                          self._emit_open_preview)
        self.menu.connect(self.delete_action,
                          SIGNAL('triggered()'),
                          self._delete_rows)
        self.menu.connect(settings_act,
                          SIGNAL('triggered()'),
                          self._emit_open_settings)
        self.menu.connect(exit_action,
                          SIGNAL('triggered()'),
                          QCoreApplication.quit)

    def toggle_horizontal_scrollbar(self, toggle):
        """Toggle horizontal scroll bar on and off.

        :param toggle: Turn scroll bar or off.
        :type toggle: bool

        :return: None
        :rtype: None
        """
        policy = Qt.ScrollBarAlwaysOff if toggle else Qt.ScrollBarAsNeeded
        self.setHorizontalScrollBarPolicy(policy)


class HistoryListItemDelegate(QStyledItemDelegate):
    """Subclass painting and style of QListView items."""

    def __init__(self, parent=None):
        super(HistoryListItemDelegate, self).__init__(parent)

        self.parent = parent

    def paint(self, painter, option, index):
        """Subclass of paint function.

        References:
        http://pydoc.net/Python/gayeogi/0.6/gayeogi.plugins.player/

        :param painter:
        :type painter: QPainter

        :param option:
        :type option: QStyleOptionViewItem

        :param index:
        :type index: QModelIndex

        :return:
        :rtype: QStyledItemDelegate.paint()
        """
        if not index.isValid():
            return QStyledItemDelegate.paint(self, painter, option, index)

        painter.save()

        # Draw selection highlight
        if option.state & QStyle.State_Selected:
            painter.setPen(QPen(option.palette.highlightedText(), 0))
            painter.fillRect(option.rect, option.palette.highlight())

        # if index.data() == 'application/x-qt-image':
        #     parent_index = QModelIndex(self.model().index(0, ID))
        #     print parent_index.column()

        # Set alignment and enable word wrap if applicable
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        if settings.get_word_wrap():
            text_option.setWrapMode(QTextOption.WrapAnywhere)
        else:
            text_option.setWrapMode(QTextOption.NoWrap)

        # Add padding to left and right side of text
        text_rect = option.rect
        text_rect.setLeft(text_rect.left() + 5)
        text_rect.setRight(text_rect.right() - 5)

        painter.drawText(text_rect, index.data(), o=text_option)
        painter.restore()

    def sizeHint(self, option, index):
        """Calculate option size.

        Calculated by creating a QTextDocument with modified text and
        determining the dimensions.

        Todo:
        * Look into using font metrics bounding rect.
        * Handle lines to display in relation to word wrap.

        References:
        http://qt-project.org/forums/viewthread/12186

        :param option:
        :type option: QStyleOptionViewItem

        :param index:
        :type index: QModelIndex

        :return:
        :rtype: QSize
        """
        if not index.isValid():
            return QStyledItemDelegate.sizeHint(self, option, index)

        doc = QTextDocument()  # Inserting self creates a memory leak!

        # Set alignment and enable word wrap if applicable
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Reimplemented as lines to display canFetchMore be ignored if word
        # wrap forces an extra line to be created
        if settings.get_word_wrap():
            text_option.setWrapMode(QTextOption.WrapAnywhere)
        else:
            text_option.setWrapMode(QTextOption.NoWrap)

        doc.setDefaultTextOption(text_option)
        doc.setPlainText(index.data())

        # Add some padding to each item, + 10
        return QSize(doc.size().width(), doc.size().height() + 5)

    # def sizeHint(self, option, index):
    #     if not index.isValid():
    #         return QStyledItemDelegate.sizeHint(self, option, index)

    #     fake_text = 'Line1\nLine2\nLine3\n'
    #     fake_fm = option.fontMetrics
    #     fake_font_rect = fake_fm.boundingRect(option.rect, Qt.AlignLeft|Qt.AlignTop|Qt.TextWordWrap, fake_text)

    #     real_text = index.data()
    #     real_fm = option.fontMetrics
    #     real_font_rect = real_fm.boundingRect(option.rect, Qt.AlignLeft|Qt.AlignTop|Qt.TextWordWrap, real_text)

    #     if real_font_rect.height() < fake_font_rect.height():
    #         height = real_font_rect.height()
    #     else:
    #         height = fake_font_rect.height()

    #     return QSize(real_font_rect.width(), height+10)

    # def flags(self, index):
    #     """Sublass of flags method.

    #     Args:
    #         index: QModelIndex
    #     """
    #     if not index.isValid():
    #         return Qt.ItemFlags()

    #     return Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
