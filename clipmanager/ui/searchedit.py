import logging

from PySide.QtCore import Qt, Slot
from PySide.QtGui import QLineEdit, QSortFilterProxyModel

from clipmanager.models import MainSqlTableModel

logger = logging.getLogger(__name__)


class SearchFilterProxyModel(QSortFilterProxyModel):
    """Search database using fixed string."""

    def __init__(self, parent=None):
        super(SearchFilterProxyModel, self).__init__(parent)

        self.setFilterKeyColumn(MainSqlTableModel.TITLE)
        self.setDynamicSortFilter(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    @Slot(str)
    def setFilterFixedString(self, *args):
        """Fetch rows from source model before filtering.

        :param args: Filter string.
        :type args: tuple[str]

        :return: None
        :rtype: None
        """
        while self.sourceModel().canFetchMore():
            self.sourceModel().fetchMore()
        QSortFilterProxyModel.setFilterFixedString(self, *args)


class SearchEdit(QLineEdit):
    """Search box for history view and main table model."""

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
                index = self.proxy.index(current_row - 1,
                                         MainSqlTableModel.TITLE_SHORT)
                self.view.setCurrentIndex(index)
            else:
                # keep selection at top
                index = self.proxy.index(0, MainSqlTableModel.TITLE_SHORT)
                self.view.setCurrentIndex(index)
        elif event.key() == Qt.Key_Down:
            current_row = self.view.currentIndex().row()
            index = self.proxy.index(current_row + 1,
                                     MainSqlTableModel.TITLE_SHORT)
            self.view.setCurrentIndex(index)
        elif event.key() == Qt.Key_Escape:
            self.clear()

        return QLineEdit.keyPressEvent(self, event)
