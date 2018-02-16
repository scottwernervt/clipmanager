import logging
from itertools import groupby
from operator import itemgetter

from PySide.QtCore import QCoreApplication, QSize, Qt, SIGNAL, Slot
from PySide.QtGui import (
    QAbstractItemView,
    QAction,
    QKeySequence,
    QListView,
    QMenu,
    QPen,
    QStyle,
    QStyledItemDelegate,
    QTextDocument,
    QTextOption,
)

from clipmanager.ui.icons import get_icon

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
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setItemDelegate(HistoryListItemDelegate(self))

        self.doubleClicked.connect(self.emit_set_clipboard)

        self.menu = QMenu(self)

        paste_action = QAction(get_icon('edit-paste'), 'Paste', self)
        paste_action.setShortcut(QKeySequence(Qt.Key_Return))
        paste_action.triggered.connect(self.emit_set_clipboard)
        self.paste_action = paste_action

        preview_action = QAction(
            get_icon('document-print-preview'),
            'Preview',
            self
        )
        preview_action.setShortcut(QKeySequence(Qt.Key_F11))
        preview_action.triggered.connect(self.emit_open_preview)
        self.preview_action = preview_action

        delete_action = QAction(get_icon('list-remove'), 'Delete', self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_item)

        exit_action = QAction(get_icon('application-exit'), 'Quit', self)
        exit_action.triggered.connect(QCoreApplication.quit)

        self.menu.addAction(paste_action)
        self.menu.addAction(preview_action)
        self.menu.addAction(delete_action)
        self.menu.addSeparator()
        self.menu.addAction(exit_action)

        # keyboard shortcuts work on selected items without menu
        self.addAction(paste_action)
        self.addAction(preview_action)
        self.addAction(delete_action)

    def resizeEvent(self, event):
        """Reset list view when word wrap setting changed.

        :param event: Resize event.
        :type event: QResizeEvent

        :return: Resize event.
        :rtype: QListView.resizeEvent
        """
        self.emit(SIGNAL('layoutChanged()'))
        self.reset()
        return QListView.resizeEvent(self, event)

    def contextMenuEvent(self, event):
        """Open context menu.

        :param event: Event.
        :type event: QEvent

        :return: None
        :rtype: None
        """
        if len(self.selectionModel().selectedIndexes()) > 1:
            self.paste_action.setDisabled(True)
            self.preview_action.setDisabled(True)
        else:
            self.paste_action.setDisabled(False)
            self.preview_action.setDisabled(False)

        self.menu.exec_(event.globalPos())

    def keyPressEvent(self, event):
        """Automatically set focus to search box when typing.

        :param event:
        :type event: QEvent

        :return:
        :rtype: QListView.keyPressEvent()
        """
        # Select all (Ctrl+A)
        if (event.modifiers() == Qt.ControlModifier) and (
                event.key() == Qt.Key_A):
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
            self.parent.search_box.setText(
                self.parent.search_box.text() + event.text())
            self.parent.search_box.setFocus(Qt.ActiveWindowFocusReason)

        return QListView.keyPressEvent(self, event)

    @Slot()
    def emit_set_clipboard(self):
        """Send set clipboard signal with current selection.

        :return: None
        :rtype: None
        """
        indexes = self.selectionModel().selectedIndexes()
        if len(indexes) == 1:
            self.emit(SIGNAL('setClipboard(QModelIndex)'), indexes[0])

    @Slot()
    def emit_open_preview(self):
        """Send open preview signal with selection index.

        :return: None
        :rtype: None
        """
        indexes = self.selectionModel().selectedIndexes()
        if len(indexes) == 1:
            self.emit(SIGNAL('openPreview(QModelIndex)'), indexes[0])

    @Slot()
    def delete_item(self):
        """Delete selected rows.

        CTRL+A on list view selects hidden columns. So even if user deselects
        an item, it will still be deleted since the hidden column is still
        selected.

        :return: None
        :rtype: None
        """
        self.setCursor(Qt.BusyCursor)

        selection_model = self.selectionModel()
        selection_rows = set(idx.row() for idx in
                             selection_model.selectedIndexes())

        # delete from data table
        parent_indexes = [self.model().index(row, 0) for row in selection_rows]
        parent_ids = filter(lambda p: p is not None,
                            [self.model().data(idx) for idx in parent_indexes])
        self.parent.data_model.delete(parent_ids)

        # delete from main table and view
        for k, g in groupby(enumerate(selection_rows), lambda (i, x): i - x):
            rows = map(itemgetter(1), g)
            self.model().removeRows(min(rows), len(rows))

        self.model().sourceModel().submitAll()
        self.unsetCursor()


class HistoryListItemDelegate(QStyledItemDelegate):
    """Subclass painting and style of QListView items."""

    def __init__(self, parent=None):
        super(HistoryListItemDelegate, self).__init__(parent)

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

        # draw selection highlight
        if option.state & QStyle.State_Selected:
            painter.setPen(QPen(option.palette.highlightedText(), 0))
            painter.fillRect(option.rect, option.palette.highlight())

        # Set alignment and enable word wrap if applicable
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_option.setWrapMode(QTextOption.NoWrap)

        # add left and right padding to text
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

        # WARNING: Inserting self creates a memory leak!
        doc = QTextDocument()

        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_option.setWrapMode(QTextOption.NoWrap)

        doc.setDefaultTextOption(text_option)
        doc.setPlainText(index.data())

        # add padding to each item
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
