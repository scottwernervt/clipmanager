import pytest
from PySide.QtCore import QAbstractListModel, QModelIndex, Qt

from clipmanager import __org__, __title__


@pytest.fixture(scope='session', autouse=True)
def config_app_settings(qapp):
    qapp.setOrganizationName('%s-pytest' % __org__.lower())
    qapp.setApplicationName('%s-pytest' % __title__.lower())


# noinspection PyShadowingNames
@pytest.fixture(scope='function')
def model():
    class Model(QAbstractListModel):
        def __init__(self, data, columns, parent=None):
            QAbstractListModel.__init__(self, parent)
            self._data = data
            self._columns = columns

        def rowCount(self, parent=QModelIndex()):
            return len(self._data)

        def columnCount(self, parent):
            return len(self._columns)

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return None
            return self._columns[section]

        def data(self, index, role=Qt.DisplayRole):
            """Override QSqlTableModel.data()

            :param index: Row and column of data entry.
            :type index: QModelIndex

            :param role:
            :type role: Qt.DisplayRole

            :return: Row column data from table.
            :rtype: str, int, or None
            """
            if not index.isValid():
                return None

            row = index.row()
            column = index.column()

            if role == Qt.DisplayRole:
                return self._data[row][column]
            elif role == Qt.ToolTipRole:
                return 'Tooltip'
            elif role == Qt.DecorationRole:
                return None

            return None

        def flags(self, index):
            if not index.isValid():
                return Qt.ItemFlags()
            return Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    model = Model([['1', 'A'], ['2', 'B'], ['3', 'C']], ['ID', 'TITLE'])
    yield model
    del model
