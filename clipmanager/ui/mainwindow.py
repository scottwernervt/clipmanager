import datetime
import logging
import zlib

from PySide.QtCore import (
    QByteArray,
    QDateTime,
    QMimeData,
    QModelIndex,
    QTextCodec,
    QTextEncoder,
    Qt,
    Signal,
    Slot,
)
from PySide.QtGui import (
    QCursor,
    QDesktopWidget,
    QGridLayout,
    QItemSelectionModel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QWidget,
)

from clipmanager import __title__, hotkey, owner, paste
from clipmanager.clipboard import ClipboardManager
from clipmanager.database import Database
from clipmanager.defs import MIME_SUPPORTED
from clipmanager.models import DataSqlTableModel, MainSqlTableModel
from clipmanager.settings import Settings
from clipmanager.ui.dialogs.preview import PreviewDialog
from clipmanager.ui.dialogs.settings import SettingsDialog
from clipmanager.ui.historylist import HistoryListView
from clipmanager.ui.icons import get_icon
from clipmanager.ui.searchedit import SearchEdit, SearchFilterProxyModel
from clipmanager.ui.systemtray import SystemTrayIcon
from clipmanager.utils import format_title, truncate_lines

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window container for main widget.

    :param minimize: True, minimize to system tray, False, bring to front.
    :type minimize: bool
    """

    def __init__(self, minimize=False):
        super(MainWindow, self).__init__()

        self.setWindowTitle(__title__)
        self.setWindowIcon(get_icon('clipmanager.ico'))

        # Remove minimize and maximize buttons from window title
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.CustomizeWindowHint |
                            Qt.WindowCloseButtonHint)

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(
                self,
                'System Tray',
                'Cannot find a system tray.'
            )

        self.system_tray = SystemTrayIcon(self)
        self.system_tray.activated.connect(self.system_tray_activate)
        self.system_tray.show()

        self.settings = Settings()

        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)

        # Return OS specific global hot key binder and set it
        self.hotkey = hotkey.initialize()
        self.paste = paste.initialize()

        if not minimize:
            self.toggle_window()

        self.register_hot_key()

        self.system_tray.toggle_window.connect(self.toggle_window)
        self.system_tray.open_settings.connect(self.open_settings)

        self.main_widget.open_settings.connect(self.open_settings)
        self.main_widget.paste_clipboard.connect(self.paste_clipboard)

    def closeEvent(self, event):
        """Capture close event and hide main window.

        Hide main window instead of exiting. Only method to quit is from right
        click menu on system tray icon or view widget.

        :param event: Exit event signal from user clicking "close".
        :type event: QCloseEvent

        :return: None
        :rtype: None
        """
        event.ignore()

        self.settings.set_window_pos(self.pos())
        self.settings.set_window_size(self.size())

        self.hide()

    def register_hot_key(self):
        """Helper function to bind global hot key to OS specific binder class.

        If binding fails then display a message in system tray notification
        tray.
        """
        key_sequence = self.settings.get_global_hot_key()  # Ctrl+Shift+h
        if key_sequence:
            self.hotkey.unregister(winid=self.winId())
            self.hotkey.register(key_sequence, self.toggle_window,
                                 self.winId())
        else:
            self.system_tray.showMessage(
                'Global Hot Key',
                'Failed to bind global hot key %s.' % hotkey,
                icon=QSystemTrayIcon.Warning,
                msecs=10000
            )

    def destroy(self):
        """Perform cleanup before exiting the application.

        :return: None
        :rtype: None
        """
        self.main_widget.destroy()

        if self.hotkey:
            self.hotkey.unregister(winid=self.winId())
            self.hotkey.destroy()

        self.settings.set_window_pos(self.pos())
        self.settings.set_window_size(self.size())
        self.settings.sync()

    @Slot(QSystemTrayIcon.ActivationReason)
    def system_tray_activate(self, activation_reason):
        """Toggle window when system tray icon is clicked.

        :param activation_reason: Clicked or double clicked.
        :type activation_reason: QSystemTrayIcon.ActivationReason.Trigger

        :return: None
        :rtype: None
        """
        if activation_reason in (QSystemTrayIcon.Trigger,
                                 QSystemTrayIcon.DoubleClick):
            self.toggle_window()

    @Slot()
    def open_settings(self):
        """Launch settings dialog.

        Before opening, unbind global hot key and rebind after dialog is closed.
        Model view is also updated to reflect lines to display.

        :return:
        :rtype:
        """
        # Windows allow's the user to open extra settings dialogs from system
        # tray menu even though dialog is modal
        self.hotkey.unregister(winid=self.winId())

        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

        self.setCursor(Qt.BusyCursor)

        # Attempt to set new hot key
        self.register_hot_key()

        self.main_widget.main_model.select()
        self.unsetCursor()

    @Slot()
    def toggle_window(self):
        """Show and hide main window.

        If visible, then hide the window. If not visible, then open window
        based on position settings at: mouse cursor, system tray, or last
        position. Adjust's the window position based on desktop dimensions to
        prevent main window going off screen.

        :return: None
        :rtype: None
        """
        window_size = self.settings.get_window_size()

        # Hide window if visible and leave function
        if self.isVisible():
            self.settings.set_window_pos(self.pos())
            self.settings.set_window_size(self.size())
            self.hide()
        else:
            # Desktop number based on cursor
            desktop = QDesktopWidget()

            # Determine global coordinates by summing screen(s) coordinates
            x_max = 0
            y_max = 999999
            for screen in range(0, desktop.screenCount()):
                x_max += desktop.availableGeometry(screen).width()

                y_screen = desktop.availableGeometry(screen).height()
                if y_screen < y_max:
                    y_max = y_screen

            # Minimum x and y screen coordinates
            x_min, y_min, __, __ = desktop.availableGeometry().getCoords()

            open_window_at = self.settings.get_open_window_at()
            if open_window_at == 2:  # 2: System tray
                x = self.system_tray.geometry().x()
                y = self.system_tray.geometry().y()
            elif open_window_at == 1:  # 1: Last position
                x = self.settings.get_window_pos().x()
                y = self.settings.get_window_pos().y()
            else:  # 0: At mouse cursor
                x = QCursor().pos().x()
                y = QCursor().pos().y()

            # Readjust window's position if offscreen
            if x < x_min:
                x = x_min
            elif x + window_size.width() > x_max:
                x = x_max - window_size.width()

            if y < y_min:
                y = y_min
            elif y + window_size.height() > y_max:
                y = y_max - window_size.height()

            # Clear search box from last interaction
            if len(self.main_widget.search_box.text()) != 0:
                self.main_widget.search_box.clear()

            # Reposition and resize the main window
            self.move(x, y)
            self.resize(window_size.width(), window_size.height())

            self.show()
            self.activateWindow()
            self.main_widget.check_selection()

    @Slot()
    def paste_clipboard(self):
        self.paste()


class MainWidget(QWidget):
    """Main widget container for main window."""
    open_settings = Signal()
    paste_clipboard = Signal()

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)

        self.parent = parent

        self.settings = Settings()

        self.database = Database(self)
        self.database.create_tables()

        self.ignore_created = False

        self.clipboard_manager = ClipboardManager(self)
        self.window_owner = owner.initialize()

        self.history_view = HistoryListView(self)

        self.main_model = MainSqlTableModel(self)
        self.data_model = DataSqlTableModel(self)

        self.search_proxy = SearchFilterProxyModel(self)
        self.search_proxy.setSourceModel(self.main_model)

        self.history_view.setModel(self.search_proxy)
        self.history_view.setModelColumn(self.main_model.TITLE_SHORT)

        self.search_box = SearchEdit(self.history_view, self.search_proxy)

        settings_button = QPushButton(self)
        settings_button.setIcon(get_icon('preferences-system'))
        settings_button.setToolTip('Settings...')
        settings_button.clicked.connect(self.emit_open_settings)

        layout = QGridLayout(self)

        layout.addWidget(self.search_box, 0, 0)
        layout.addWidget(settings_button, 0, 1)
        layout.addWidget(self.history_view, 1, 0, 1, 2)

        self.setLayout(layout)

        self.clipboard_manager.new_item.connect(self.new_item)

        self.search_box.returnPressed.connect(self.set_clipboard)
        self.search_box.textChanged.connect(
            self.search_proxy.setFilterFixedString)
        self.search_box.textChanged.connect(self.check_selection)

        self.history_view.set_clipboard.connect(self.set_clipboard)
        self.history_view.open_preview.connect(self.open_preview)

    def create_item_title(self, mime_data):
        """Create full title from clipboard mime data.

        Extract a title from QMimeData using urls, html, or text.

        :param mime_data:
        :type mime_data: QMimeData

        :return: Full title or None if it did not have any text/html/url.
        :rtype: str or None
        """
        if mime_data.hasUrls():
            urls = [url.toString() for url in mime_data.urls()]
            return 'Copied File(s):\n' + '\n'.join(urls)
        elif mime_data.hasText():
            return mime_data.text()
        elif mime_data.hasHtml():  # last resort
            return mime_data.html()
        else:
            self.parent.system_tray.showMessage(
                'Clipboard',
                'Failed to get clipboard mime data formats.',
                icon=QSystemTrayIcon.Warning,
                msecs=5000
            )
            return None

    def get_item_checksum(self, mime_data):
        """Calculate CRC checksum based on urls, html, or text.

        :param mime_data: Data from clipboard.
        :type mime_data: QMimeData

        :return: CRC32 checksum.
        :rtype: int
        """
        if mime_data.hasUrls():
            checksum_str = str(mime_data.urls())
        elif mime_data.hasHtml():
            checksum_str = mime_data.html()
        elif mime_data.hasText():
            checksum_str = mime_data.text()
        else:
            self.parent.system_tray.showMessage(
                'Clipboard',
                'Failed to get clipboard text/html/urls.',
                icon=QSystemTrayIcon.Warning,
                msecs=5000
            )
            return None

        # encode unicode characters for crc library
        codec = QTextCodec.codecForName('UTF-8')
        encoder = QTextEncoder(codec)
        byte_array = encoder.fromUnicode(checksum_str)  # QByteArray

        checksum = zlib.crc32(byte_array)
        return checksum

    def destroy(self):
        self.main_model.submitAll()
        self.database.close()

    def find_duplicate(self, checksum):
        """Checks for a duplicate row in Main table.

        :param checksum: CRC32 string to search for.
        :type checksum: int

        :return: True if duplicate found and False if not found.
        :rtype: bool
        """
        for row in range(self.main_model.rowCount()):
            source_index = self.main_model.index(row, self.main_model.CHECKSUM)
            checksum_source = self.main_model.data(source_index)

            # update row created_at timestamp
            if str(checksum) == str(checksum_source):
                self.main_model.setData(
                    self.main_model.index(row, self.main_model.CREATED_AT),
                    QDateTime.currentMSecsSinceEpoch()
                )
                self.main_model.submitAll()
                return True

        return False

    def purge_expired_entries(self):
        """Remove entries that have expired.

        Starting at the bottom of the list, compare each item's date to user
        set expire in X days. If item is older than setting, remove it from
        database.

        :return: None
        :rtype: None
        """
        expire_at = self.settings.get_expire_value()
        if int(expire_at) == 0:
            return

        entries = range(0, self.main_model.rowCount())
        entries.reverse()  # sort by oldest

        for row in entries:
            index = self.main_model.index(row, self.main_model.CREATED_AT)
            created_at = self.main_model.data(index)

            # Convert from ms to s
            time = datetime.datetime.fromtimestamp(created_at / 1000)
            today = datetime.datetime.today()
            delta = today - time

            if delta.days > expire_at:
                index = self.main_model.index(row, self.main_model.ID)
                parent_id = self.main_model.data(index)

                self.database.delete_mime(parent_id)
                self.main_model.removeRow(row)
            else:
                break

        self.main_model.submitAll()

    def purge_max_entries(self):
        """Remove extra entries.

        Count total number of items in history, and if greater than user
        setting for maximum entries, delete_item them.

        :return: None
        :rtype: None
        """
        max_entries = self.settings.get_max_entries_value()
        if max_entries == 0:
            return

        row_count = self.main_model.rowCount() + 1

        if row_count > max_entries:
            for row in range(max_entries - 1, row_count):
                index_id = self.main_model.index(row, self.main_model.ID)
                parent_id = self.main_model.data(index_id)

                self.data_model.delete(parent_id)
                self.main_model.removeRow(row)

        self.main_model.submitAll()

    @Slot(str)
    def check_selection(self):
        """Prevent user selection from disappearing during a proxy filter.

        :return: None
        :rtype: None
        """
        selection_model = self.history_view.selectionModel()
        indexes = selection_model.selectedIndexes()

        if not indexes:
            index = self.search_proxy.index(0, self.main_model.TITLE_SHORT)
            selection_model.select(index, QItemSelectionModel.Select)
            selection_model.setCurrentIndex(index,
                                            QItemSelectionModel.Select)

    @Slot(QMimeData)
    def new_item(self, mime_data):
        """Append clipboard contents to database.

        :param mime_data: Clipboard contents mime data
        :type mime_data: QMimeData

        :return: True, if successfully added.
        :rtype: bool
        """
        if self.settings.get_disconnect():
            return False
        elif self.ignore_created:
            self.ignore_created = False
            return False

        # Check if process that set clipboard is on exclude list
        window_names = self.window_owner()
        logger.debug('%s', window_names)

        ignore_list = self.settings.get_exclude().lower().split(';')
        if any(str(i) in window_names for i in ignore_list):
            logger.info('Ignoring copy from application.')
            return False

        title = self.create_item_title(mime_data)
        if not title:
            self.parent.system_tray.showMessage(
                'Clipboard',
                'Failed to get clipboard contents.',
                icon=QSystemTrayIcon.Warning,
                msecs=5000
            )
            return None

        title_short = format_title(title)
        title_short = truncate_lines(title_short,
                                     self.settings.get_lines_to_display())
        created_at = QDateTime.currentMSecsSinceEpoch()

        checksum = self.get_item_checksum(mime_data)
        if checksum and self.find_duplicate(checksum):
            return None

        parent_id = self.main_model.create(title=title,
                                           title_short=title_short,
                                           checksum=checksum,
                                           created_at=created_at)

        for mime_format in MIME_SUPPORTED:
            if mime_data.hasFormat(mime_format):
                byte_data = QByteArray(mime_data.data(mime_format))
                self.data_model.create(parent_id, mime_format, byte_data)

        self.purge_max_entries()
        self.purge_expired_entries()

        # Highlight top item and then insert mime data
        self.main_model.select()  # Update view
        index = QModelIndex(
            self.history_view.model().index(0, self.main_model.TITLE_SHORT)
        )
        self.history_view.setCurrentIndex(index)

        return True

    @Slot(QModelIndex)
    def open_preview(self, selection_index):
        """"Open preview dialog for selected item.

        :param selection_index: Selected row index from history list view.
        :type selection_index: QModelIndex

        :return: None
        :rtype: None
        """
        source_index = self.search_proxy.mapToSource(selection_index)
        source_row = source_index.row()
        model_index = self.main_model.index(source_row, self.main_model.ID)
        parent_id = self.main_model.data(model_index)

        mime_data = QMimeData()
        for mime_format, byte_data in self.data_model.read(parent_id):
            mime_data.setData(mime_format, byte_data)

        preview_dialog = PreviewDialog(mime_data, self)
        preview_dialog.exec_()
        del preview_dialog

    @Slot(QModelIndex)
    def set_clipboard(self, selection_index):
        """Set selection item to clipboard.

        :param selection_index:
        :type selection_index:

        :return:
        :rtype:
        """
        self.window().hide()
        self.ignore_created = True

        source_index = self.search_proxy.mapToSource(selection_index)
        source_row = source_index.row()
        model_index = self.main_model.index(source_row, self.main_model.ID)
        parent_id = self.main_model.data(model_index)

        mime_data = QMimeData()
        for mime_type, byte_data in self.data_model.read(parent_id):
            mime_data.setData(mime_type, byte_data)

        self.clipboard_manager.set_text(mime_data)

        if self.settings.get_send_paste():
            self.paste_clipboard.emit()

        self.main_model.setData(
            self.main_model.index(model_index.row(),
                                  self.main_model.CREATED_AT),
            QDateTime.currentMSecsSinceEpoch())
        self.main_model.submitAll()

    @Slot()
    def emit_open_settings(self):
        """Emit signal to open settings dialog.

        :return: None
        :rtype: None
        """
        self.open_settings.emit()
