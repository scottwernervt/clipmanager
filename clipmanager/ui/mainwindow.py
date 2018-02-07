import datetime
import logging

from PySide.QtCore import (
    QByteArray,
    QDateTime,
    QMimeData,
    QModelIndex,
    Qt,
    SIGNAL,
    Slot,
)
from PySide.QtGui import (
    QCursor,
    QDesktopWidget,
    QGridLayout,
    QIcon,
    QItemSelectionModel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QWidget,
)

from clipmanager import hotkey, owner, paste
from clipmanager.clipboard import ClipboardManager
from clipmanager.database import (
    create_connection,
    create_tables,
    delete_mime,
    get_mime,
    insert_data,
    insert_main,
)
from clipmanager.defs import (
    APP_NAME,
    CHECKSUM,
    CREATED_AT,
    ID,
    MIME_SUPPORTED,
    STORAGE_PATH,
    TITLE_SHORT,
)
from clipmanager.model import MainSqlTableModel
from clipmanager.settings import settings
from clipmanager.ui.dialogs.preview import PreviewDialog
from clipmanager.ui.dialogs.settings import SettingsDialog
from clipmanager.ui.historylist import HistoryListView
from clipmanager.ui.searchbox import SearchBox, SearchFilterProxyModel
from clipmanager.ui.systemtray import SystemTrayIcon
from clipmanager.utils import (
    calculate_checksum,
    create_full_title,
    format_title,
    remove_extra_lines,
    resource_filename,
)

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window container for main widget.
    """

    def __init__(self, minimize=False):
        """Initialize main window, systemtray, global hotkey, and signals.

        Args:
            minimize: True, minimize to system tray.
                      False, bring window to front.
        """
        super(MainWindow, self).__init__()

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(resource_filename('icons/clipmanager.ico')))

        # Remove minimize and maximize buttons from window title
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.CustomizeWindowHint |
                            Qt.WindowCloseButtonHint)

        # Connect to database and create tables
        self.db = create_connection(STORAGE_PATH)
        create_tables()

        # Create main widget that holds contents of clipboard history
        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)

        # Create system tray icon
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warn('cannot find a system tray.')
            QMessageBox.warning(self, 'System Tray',
                                'Cannot find a system tray.')

        self.tray_icon = SystemTrayIcon(self)
        self.tray_icon.activated.connect(self._on_icon_activated)
        self.tray_icon.show()

        # Return OS specific global hot key binder and set it
        self._hotkey = hotkey.initialize()
        self._paste = paste.initialize()

        # Toggle window from system tray right click menu
        self.connect(self.tray_icon, SIGNAL('toggleWindow()'),
                     self._on_toggle_window)

        # Open settings dialog from right click menu on system tray and view
        self.connect(self.tray_icon, SIGNAL('openSettings()'),
                     self._on_open_settings)

        self.connect(self.main_widget, SIGNAL('openSettings()'),
                     self._on_open_settings)

        self.connect(self.main_widget, SIGNAL('pasteClipboard()'),
                     self._paste)

        # Show window
        if not minimize:
            self._on_toggle_window()

        self.register_hot_key()

    def closeEvent(self, event):
        """Capture close event and hide main window.

        Hide main window instead of exiting. Only method to quit is from right 
        click menu on system tray icon or view widget.

        Args:
            event (QCloseEvent): Close event from OS requested exit like 
                ALT+F4, clicking X on window title bar, etc. 
        """
        event.ignore()

        # Store window position and size
        settings.set_window_pos(self.pos())
        settings.set_window_size(self.size())

        self.hide()

    def destroy(self):
        """Perform actions before exiting the application.

        Following actions are performed before exit: unbind global hot key, 
        save window position and size, submit all changes to model, and close 
        database connection.
        """
        if self._hotkey:
            self._hotkey.unregister(winid=self.winId())
            self._hotkey.destroy()

        settings.set_window_pos(self.pos())
        settings.set_window_size(self.size())
        settings.sync()

        self.main_widget.model_main.submitAll()
        self.db.close()

    @Slot(QSystemTrayIcon.ActivationReason)
    def _on_icon_activated(self, reason):
        """Bring main window to front if system tray clicked.
   
        Args:
            reason (QSystemTrayIcon.ActivationReason.Trigger): Clicked and 
                double clicked.
        """
        if reason in (QSystemTrayIcon.Trigger,
                      QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                self.show()  # Open window
                self.activateWindow()  # Bring to front
            else:
                self._on_toggle_window()

    @Slot()
    def _on_open_settings(self):
        """Open settings dialog.

        Prior to opening dialog, the global hot key is unbinded and then binded 
        in case user changes it. The model view is updated to reflect changes 
        in lines to display and if word wrap is enabled.
        """
        # Windows allow's the user to open extra settings dialogs from system
        # tray menu even though dialog is modal
        self._hotkey.unregister(winid=self.winId())

        # PreviewDialog(self) so it opens at main window
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

        self.setCursor(Qt.BusyCursor)

        # Attempt to set new hot key
        self.register_hot_key()

        # Update scroll bars and refresh view
        set_word_wrap = settings.get_word_wrap()
        self.main_widget.view_main.toggle_horizontal_scrollbar(set_word_wrap)
        self.main_widget.model_main.select()

        self.unsetCursor()

    @Slot()
    def _on_toggle_window(self):
        """Toggle the main window visibility.

        If visible, then hide the window. If not visible, then open window 
        based on position settings at: mouse cursor, system tray, or last 
        position. Adjust's the window position based on desktop dimensions to 
        prevent main window going off screen.

        TODO: Clean up this code as it is long and can most likely be improved.
        """
        win_size = settings.get_window_size()  # QSize()

        # Hide window if visible and leave function
        if self.isVisible():
            # Store window position and size
            settings.set_window_pos(self.pos())
            settings.set_window_size(self.size())

            self.hide()
        else:
            # Desktop number based on cursor
            desktop = QDesktopWidget()
            current_screen = desktop.screenNumber(QCursor().pos())
            logger.debug('Screen #=%s' % current_screen)

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
            logger.debug('GlobalScreenRect=(%d,%d,%d,%d)' % (x_min, y_min,
                                                             x_max, y_max))

            # 2: System tray
            if settings.get_open_window_at() == 2:
                x = self.tray_icon.geometry().x()
                y = self.tray_icon.geometry().y()
                logger.debug('SystemTrayCoords=(%d,%d)' % (x, y))

            # 1: Last position
            elif settings.get_open_window_at() == 1:
                x = settings.get_window_pos().x()
                y = settings.get_window_pos().y()
                logger.debug('LastPositionCoords=(%d,%d)' % (x, y))

            # 0: At mouse cursor
            else:
                x = QCursor().pos().x()
                y = QCursor().pos().y()
                logger.debug('CursorCoords=(%d,%d)' % (x, y))

            # Readjust window's position if it will be off screen
            if x < x_min:
                x = x_min
            elif x + win_size.width() > x_max:
                x = x_max - win_size.width()

            if y < y_min:
                y = y_min
            elif y + win_size.height() > y_max:
                y = y_max - win_size.height()

            # Clear search box from last interaction
            if len(self.main_widget.search_box.text()) != 0:
                self.main_widget.search_box.clear()

            logger.debug('MainWindowCoords=(%d,%d)' % (x, y))
            logger.debug('MainWindowSize=(%d,%d)' % (win_size.width(),
                                                     win_size.height()))

            # Reposition and resize the main window
            self.move(x, y)
            self.resize(win_size.width(), win_size.height())

            self.show()  # Open window
            self.activateWindow()  # Bring to front
            self.main_widget.check_selection()

    @Slot()
    def paste_action(self):
        self._paste()

    def register_hot_key(self):
        """Helper function to bind global hot key to OS specific binder class.

        If binding fails then display a message in system tray notification 
        tray.
        """
        key_sequence = settings.get_global_hot_key()  # Ctrl+Shift+h
        if key_sequence:
            self._hotkey.unregister(winid=self.winId())
            self._hotkey.register(key_sequence, self._on_toggle_window,
                                  self.winId())
        else:
            title = 'Global Hot Key'
            message = 'Failed to bind global hot key %s.' % hotkey
            self.tray_icon.showMessage(title, message,
                                       icon=QSystemTrayIcon.Warning,
                                       msecs=10000)


class MainWidget(QWidget):
    """Main widget container for main window."""

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.parent = parent

        # Ignore clipboard change when user sets item to clipboard
        self.ignore_created = False

        self.clipboard_manager = ClipboardManager(self)
        self.window_owner = owner.initialize()

        # Create view, model, and proxy
        self.view_main = HistoryListView(self)
        self.model_main = MainSqlTableModel(self)

        self.proxy_main = SearchFilterProxyModel(self)
        self.proxy_main.setSourceModel(self.model_main)

        # self.proxy_main = QSortFilterProxyModel(self)
        # self.proxy_main.setFilterKeyColumn(TITLE)
        # self.proxy_main.setSourceModel(self.model_main)
        # self.proxy_main.setDynamicSortFilter(True)
        # self.proxy_main.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.view_main.setModel(self.proxy_main)
        self.view_main.setModelColumn(TITLE_SHORT)

        # Pass view and proxy pointers to search box class
        self.search_box = SearchBox(self.view_main, self.proxy_main)

        settings_button = QPushButton(self)
        settings_button.setIcon(QIcon.fromTheme('emblem-system',
                                                QIcon(
                                                    resource_filename(
                                                        'icons/settings.png')
                                                )))
        settings_button.setToolTip('Settings...')

        # Create layout
        layout = QGridLayout(self)
        layout.addWidget(self.search_box, 0, 0)
        layout.addWidget(settings_button, 0, 1)
        layout.addWidget(self.view_main, 1, 0, 1, 2)
        self.setLayout(layout)

        # Set clipboard contents if return pressed or from right click menu
        self.connect(self.search_box, SIGNAL('returnPressed()'),
                     self.on_set_clipboard)

        # Search proxy model
        self.connect(self.search_box, SIGNAL('textChanged(QString)'),
                     self.proxy_main.setFilterFixedString)

        # Check selection in view during search
        self.connect(self.search_box, SIGNAL('textChanged(QString)'),
                     self.check_selection)

        # Set clipboard data from signal by view
        self.connect(self.view_main, SIGNAL('setClipboard()'),
                     self.on_set_clipboard)

        # Open settings dialog from button next to search box
        self.connect(settings_button, SIGNAL('clicked()'),
                     self._emit_open_settings)

        # Open settings dialog from right click menu of the view
        self.connect(self.view_main, SIGNAL('openSettings()'),
                     self._emit_open_settings)

        # Show preview of selected item in view
        self.connect(self.view_main,
                     SIGNAL('openPreview(QModelIndex)'),
                     self._on_open_preview)

        # Clipboard dataChanged() emits to append new item to model->view
        self.connect(self.clipboard_manager,
                     SIGNAL('newItem(QMimeData)'), self.on_new_item)

    @Slot(str)
    def check_selection(self, text=None):
        """Prevents selection from disappearing during proxy filter.

        Args:
            text (str): Ignored parameter as the signal emits it.
        """
        selection_model = self.view_main.selectionModel()
        indexes = selection_model.selectedIndexes()

        if not indexes:
            index = self.proxy_main.index(0, TITLE_SHORT)
            selection_model.select(index, QItemSelectionModel.Select)
            selection_model.setCurrentIndex(index,
                                            QItemSelectionModel.Select)

    @Slot()
    def _emit_open_settings(self):
        """Emit signal to open settings dialog.
        """
        self.emit(SIGNAL('openSettings()'))

    def find_duplicate(self, checksum):
        """Checks for a duplicate row in Main table.

        Searches entire model for a duplicate checksum on new item that 
        requested to be created. If duplicate is found then update the source 
        CREATED_AT column and submit changes.

        Args:
            checksum (str): CRC32 string to search for.

        Returns:
            True (bool): Matching row found and date updated.
            False (bool): No matching row found.

        TODO: Investigate if SQL query is quicker on larger databases.
        """
        for row in range(self.model_main.rowCount()):
            # Get CHECKSUM column from source's row
            source_index = self.model_main.index(row, CHECKSUM)
            checksum_source = self.model_main.data(source_index)

            # Update CREATED_AT column if checksums match
            if str(checksum) == str(checksum_source):
                logger.debug('%s == %s' % (checksum, checksum_source))

                self.model_main.setData(self.model_main.index(row, CREATED_AT),
                                        QDateTime.currentMSecsSinceEpoch())
                self.model_main.submitAll()
                logger.info(True)
                return True

        logger.info(False)

        return False

    @Slot(QMimeData)
    def on_new_item(self, mime_data):
        """Append new clipboard contents to database.

        Performs checksum for new data vs database. If duplicate found, then 
        the time is updated in a separate function. Once parent data is
        created, the mime data is converted to QByteArray and stored in data 
        table as a blob.

        Args:
            mime_data (QMimeData): clipboard contents mime data

        Returns: 
            True (bool): Successfully added data to model.
            None: User just set new clipboard data trigger dataChanged() to be
                emitted. Data does not have any text. Duplicate found. Storing
                data in database fails.

        TODO: Clean up this function as there are too many random returns. 
            Store images.
        """
        # Do not perform the new item process because user just set clipboard 
        # contents
        if self.ignore_created:
            self.ignore_created = False
            return None

        # Check if process that set clipboard is on exclude list
        window_names = self.window_owner()
        ignore_list = settings.get_exclude().lower().split(';')
        if any(str(i) in window_names for i in ignore_list):
            logger.info('Ignoring copy action from application.')
            return None

        title = create_full_title(mime_data)
        title_short = format_title(title)
        title_short = remove_extra_lines(title_short,
                                         settings.get_lines_to_display())
        created_at = QDateTime.currentMSecsSinceEpoch()

        checksum = calculate_checksum(mime_data)
        if checksum and self.find_duplicate(checksum):
            # TODO: Update created_at date for duplicate
            return None

        parent_id = insert_main(title=title,
                                title_short=title_short,
                                checksum=checksum,
                                created_at=created_at)

        # Save each mime format as QByteArray to data table.
        for mime_format in MIME_SUPPORTED:
            if mime_data.hasFormat(mime_format):
                byte_data = QByteArray(mime_data.data(mime_format))
                logger.debug('Mime format: %s', mime_format)
                insert_data(parent_id, mime_format, byte_data)

        self.purge_max_entries()
        self.purge_expired_entries()

        # Highlight top item and then insert mime data
        self.model_main.select()  # Update view
        index = QModelIndex(self.view_main.model().index(0, TITLE_SHORT))
        self.view_main.setCurrentIndex(index)

        return True

    def purge_expired_entries(self):
        """Remove entries that have expired.

        Starting at the bottom of the list, compare each item's date to user 
        set expire in X days. If item is older than setting, remove it from
        database.
        """
        # Work in reverse and break when row date is less than
        # expiration date
        expire_at = settings.get_expire_value()
        if int(expire_at) == 0:
            return

        entries = range(0, self.model_main.rowCount())
        entries.reverse()  # Start from bottom of QListView

        for row in entries:
            logger.debug('Row: %d' % row)
            index = self.model_main.index(row, CREATED_AT)
            created_at = self.model_main.data(index)
            logger.debug('Date: %s' % created_at)

            # Convert from ms to s
            time = datetime.datetime.fromtimestamp(created_at / 1000)
            today = datetime.datetime.today()
            delta = today - time

            logger.debug('Delta: %d days' % delta.days)
            if delta.days > expire_at:
                index = self.model_main.index(row, ID)
                parent_id = self.model_main.data(index)

                delete_mime(parent_id)
                self.model_main.removeRow(row)
            else:
                logger.debug('Last row not expired, breaking!')
                break

        self.model_main.submitAll()

    def purge_max_entries(self):
        """Remove extra entries.

        Count total number of items in history, and if greater than user
        setting for maximum entries, delete them.
        """
        max_entries = settings.get_max_entries_value()
        if max_entries == 0:
            return

        row_count = self.model_main.rowCount() + 1

        logger.debug('Row count: %s' % row_count)
        logger.debug('Max entries: %s' % max_entries)

        if row_count > max_entries:
            # Delete extra rows
            # self.model_main.removeRows(max_entries, row_count-max_entries)
            for row in range(max_entries - 1, row_count):
                logger.debug('Row: %d' % row)

                index_id = self.model_main.index(row, ID)
                parent_id = self.model_main.data(index_id)

                delete_mime(parent_id)
                self.model_main.removeRow(row)

        self.model_main.submitAll()

    @Slot(QModelIndex)
    def _on_open_preview(self, index):
        """Open preview dialog of selected item.

        Args:
            index (QModelIndex): Selected row index from view
        """
        # Map the view->proxy to the source->db index
        source_index = self.proxy_main.mapToSource(index)

        # No item is selected so quit
        index_id = self.model_main.index(source_index.row(), ID)
        if index_id.row() <= -1:
            return None

        parent_id = self.model_main.data(index_id)
        logger.debug('ID: %s' % parent_id)

        # Find all children relating to parent_id
        mime_list = get_mime(parent_id)

        # Create QMimeData object based on formats and byte data
        mime_data = QMimeData()
        for mime_format, byte_data in mime_list:
            mime_data.setData(mime_format, byte_data)

        # PreviewDialog(self) so it opens at main window
        preview_dialog = PreviewDialog(self)
        preview_dialog.setup_ui(mime_data)
        preview_dialog.exec_()

    @Slot()
    def on_set_clipboard(self):
        """Set clipboard contents from list selection.
        
        Parent ID is retrieved from user selection and mime data is compiled 
        from database search. QMimeData() object is created from bytearray and 
        reference format. Finally, clipboard contents are set, window is 
        hidden, and OS paste command is sent to current active window.

        When clipboard contents are set, it emits dataChanged() so the app
        immediately attempts to insert it and runs into a duplicate update.
        Setting ignore_created will prevent this check from happening.
        """
        self.ignore_created = True

        # Hide parent window
        self.window().hide()

        # Map the view->proxy to the source->db index
        proxy_index = self.view_main.currentIndex()
        source_index = self.proxy_main.mapToSource(proxy_index)

        # Get parent ID by creating a new index for data
        model_index = self.model_main.index(source_index.row(), ID)
        parent_id = self.model_main.data(model_index)

        # Find all childs relating to parent_id
        mime_list = get_mime(parent_id)

        # Create QMimeData object based on formats and byte data
        mime_data = QMimeData()
        for mime_type, byte_data in mime_list:
            mime_data.setData(mime_type, byte_data)

        # Set to clipboard
        self.clipboard_manager.set_text(mime_data)

        # Send Ctrl+V key stroke (paste) to foreground window
        if settings.get_send_paste():
            self.emit(SIGNAL('pasteClipboard()'))

        # Update the date column in source
        self.model_main.setData(
            self.model_main.index(model_index.row(), CREATED_AT),
            QDateTime.currentMSecsSinceEpoch())
        self.model_main.submitAll()
