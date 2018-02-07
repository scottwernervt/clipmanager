import logging

from PySide.QtCore import Qt, Slot
from PySide.QtGui import QLineEdit, QSortFilterProxyModel

from clipmanager.defs import TITLEFULL, TITLESHORT

logger = logging.getLogger(__name__)


class SearchFilterProxyModel(QSortFilterProxyModel):
    """Search database using fixed string.
    """

    def __init__(self, parent=None):
        super(SearchFilterProxyModel, self).__init__()

        self.setFilterKeyColumn(TITLEFULL)
        self.setDynamicSortFilter(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    @Slot(str)
    def setFilterFixedString(self, *args):
        """Fetch more rows from the source model before filtering the QListView.
        
        Args:
            *args: tuple with a unicode string, (u'string',)
        """
        # Issue #1: QSortFilterProxyModel does not show all matching records 
        # due to all records not being loaded until scrolled.
        # while self.sourceModel().canFetchMore():
        #     self.sourceModel().fetchMore()
        QSortFilterProxyModel.setFilterFixedString(self, args[0])


class SearchBox(QLineEdit):
    """Search box for history model.

    Todo:
        See if there is a better way than passing references to view and proxy
        models.
    """

    def __init__(self, view, proxy, parent=None):
        super(SearchBox, self).__init__(parent)
        self.view = view  # QListView
        self.proxy = proxy  # QSortFilterProxyModel
        self.parent = parent

        self.setPlaceholderText('Start typing to search history...')

    def keyPressEvent(self, event):
        """Allow up and down navigation on list from search box.

        Sub class to enable list navigiation when searching in the text box.
        Must return False at end of all events will be blocked.

        Args:
            event: Qt.Event

        Returns:
            Allow other events to process after conditional checks.
        """
        # Change selected row by moving up
        if event.key() == Qt.Key_Up:
            if self.view.currentIndex().row() >= 1:
                current_row = self.view.currentIndex().row()
                index = self.proxy.index(current_row - 1, TITLESHORT)
                self.view.setCurrentIndex(index)
            else:
                # Prevent user from going off list (keep them at top)
                index = self.proxy.index(0, TITLESHORT)
                self.view.setCurrentIndex(index)

        # Change selected row by moving down
        elif event.key() == Qt.Key_Down:
            current_row = self.view.currentIndex().row()
            index = self.proxy.index(current_row + 1, TITLESHORT)
            self.view.setCurrentIndex(index)

        # Clear text
        elif event.key() == Qt.Key_Escape:
            self.clear()

        return QLineEdit.keyPressEvent(self, event)
