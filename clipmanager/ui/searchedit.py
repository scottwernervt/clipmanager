import logging

from PySide.QtCore import Qt, Slot
from PySide.QtGui import QLineEdit, QSortFilterProxyModel

from clipmanager.defs import TITLE, TITLE_SHORT

logger = logging.getLogger(__name__)


class SearchFilterProxyModel(QSortFilterProxyModel):
    """Search database using fixed string."""

    def __init__(self, parent=None):
        super(SearchFilterProxyModel, self).__init__(parent)

        self.setFilterKeyColumn(TITLE)
        self.setDynamicSortFilter(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    @Slot(str)
    def setFilterFixedString(self, *args):
        """Fetch rows from source model before filtering.

        TODO: QSortFilterProxyModel does not show all matching records due to
        all records not being loaded until scrolled.

        :param args: Filter string.
        :type args: tuple[str]

        :return: None
        :rtype: None
        """
        # while self.sourceModel().canFetchMore():
        #     self.sourceModel().fetchMore()
        QSortFilterProxyModel.setFilterFixedString(self, *args)


class SearchEdit(QLineEdit):
    """Search box for history model.

    Todo:
        See if there is a better way than passing references to view and proxy
        models.
    """

    def __init__(self, view, proxy, parent=None):
        super(SearchEdit, self).__init__(parent)
        self.view = view  # QListView
        self.proxy = proxy  # QSortFilterProxyModel
        self.parent = parent

        self.setPlaceholderText('Start typing to search history...')

    def keyPressEvent(self, event):
        """Allow arrow selection on history list from search box.

        Override QLineEdit.keyPressEvent and check for up and down arrow key
        for changing selection. If conditional checks not met, return original
        keyPressEvent.

        :param event:
        :type event: Qt.Event

        :return: None
        :rtype: None
        """
        if event.key() == Qt.Key_Up:
            if self.view.currentIndex().row() >= 1:
                current_row = self.view.currentIndex().row()
                index = self.proxy.index(current_row - 1, TITLE_SHORT)
                self.view.setCurrentIndex(index)
            else:
                # keep selection at top
                index = self.proxy.index(0, TITLE_SHORT)
                self.view.setCurrentIndex(index)
        elif event.key() == Qt.Key_Down:
            current_row = self.view.currentIndex().row()
            index = self.proxy.index(current_row + 1, TITLE_SHORT)
            self.view.setCurrentIndex(index)
        elif event.key() == Qt.Key_Escape:
            self.clear()

        return QLineEdit.keyPressEvent(self, event)
