#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import sys

from PySide import QtCore
from PySide import QtGui

import clipboards
import database
import dialogs
from defs import APP_NAME
from defs import CHECKSUM
from defs import DATE
from defs import ID
from defs import MIME_REFERENCES
from defs import TITLESHORT
from defs import TITLEFULL
from defs import STORAGE_PATH
import model
import searchbox
from settings import settings
import systemtray
import view
import utils

# Platform dependent package.modules: paste and global hot key binder
if sys.platform.startswith('win32'):
    import paste.win32 as paste
    import hotkey.win32 as hotkey
elif sys.platform.startswith('linux'):
    import paste.linux as paste
    import hotkey.linux as hotkey
else:
    logging.warn('Cannot paste to platform: %s' % sys.platform)

logging.getLogger(__name__)


class MainWindow(QtGui.QMainWindow):
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
        self.setWindowIcon(QtGui.QIcon(utils.resource_filename('icons/clipmanager.ico')))

        # Remove minimize and maximize buttons from window title
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|
                            QtCore.Qt.CustomizeWindowHint|
                            QtCore.Qt.WindowCloseButtonHint)

        # Connect to database and create tables
        self.db = database.create_connection(STORAGE_PATH)
        database.create_tables()

        # Create main widget that holds contents of clipboard history
        self.main_widget = MainWidget(self) 
        self.setCentralWidget(self.main_widget)

        # Create system tray icon
        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            logging.warn('cannot find a system tray.')
            QtGui.QMessageBox.warning(self, 'System Tray',
                                      'Cannot find a system tray.')
        
        self.tray_icon = systemtray.SystemTrayIcon(self)
        self.tray_icon.activated.connect(self._on_icon_activated)
        self.tray_icon.show()

        # Return OS specific global hot key binder and set it
        self.key_binder = hotkey.Binder(self)
        self._set_hot_key()

        # Toggle window from system tray right click menu
        self.connect(self.tray_icon, QtCore.SIGNAL('toggle-window()'),
                     self._on_toggle_window)

        # Open settings dialog from right click menu on system tray and view
        self.connect(self.tray_icon, QtCore.SIGNAL('open-settings()'), 
                     self._on_open_settings)

        self.connect(self.main_widget, QtCore.SIGNAL('open-settings()'), 
                     self._on_open_settings)

        # Show window
        if not minimize:
            self._on_toggle_window()

    def closeEvent(self, event):
        """Capture close event and hide main window.

        Hide main window instead of exiting. Only method to quit is from right 
        click menu on system tray icon or view widget.

        Args:
            event (QtGui.QCloseEvent): Close event from OS requested exit like 
                ALT+F4, clicking X on window title bar, etc. 
        """
        event.ignore()

        # Store window position and size
        settings.set_window_pos(self.pos())
        settings.set_window_size(self.size())

        self.hide()
        
    def clean_up(self):
        """Perform actions before exiting the application.

        Following actions are performed before exit: unbind global hot key, 
        save window position and size, submit all changes to model, and close 
        database connection.
        """
        logging.debug('Unbinding global hot key.')
        self.key_binder.unbind(settings.get_global_hot_key())

        logging.debug('Saving window size and position.')
        settings.set_window_pos(self.pos())
        settings.set_window_size(self.size())
        settings.sync()

        logging.debug('Submitting changes to model.')
        self.main_widget.model_main.submitAll()
        
        logging.debug('Closing model.')
        self.db.close()

    @QtCore.Slot(QtGui.QSystemTrayIcon.ActivationReason)
    def _on_icon_activated(self, reason):
        """Bring main window to front if system tray clicked.
   
        Args:
            reason (QSystemTrayIcon.ActivationReason.Trigger): Clicked and 
                double clicked.
        """
        if reason in (QtGui.QSystemTrayIcon.Trigger,
                      QtGui.QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                self.show()             # Open window
                self.activateWindow()   # Bring to front
            else:
                self._on_toggle_window()
    
    @QtCore.Slot()
    def _on_open_settings(self):
        """Open settings dialog.

        Prior to opening dialog, the global hot key is unbinded and then binded 
        in case user changes it. The model view is updated to reflect changes 
        in lines to display and if word wrap is enabled.
        """
        # Windows allow's the user to open extra settings dialogs from system
        # tray menu even though dialog is modal
        try:
            self.key_binder.unbind(settings.get_global_hot_key())
        except AttributeError:
            return None

        # PreviewDialog(self) so it opens at main window
        settings_dialog = dialogs.SettingsDialog(self)
        settings_dialog.exec_()

        self.setCursor(QtCore.Qt.BusyCursor)

        # Attempt to set new hot key
        self._set_hot_key()

        # Update scroll bars and refresh view
        set_word_wrap = settings.get_word_wrap()
        self.main_widget.view_main.set_horiz_scrollbar(set_word_wrap)
        self.main_widget.model_main.select()

        self.unsetCursor()

    @QtCore.Slot()
    def _on_toggle_window(self):
        """Toggle the main window visibility.

        If visible, then hide the window. If not visible, then open window 
        based on position settings at: mouse cursor, system tray, or last 
        position. Adjust's the window position based on desktop dimensions to 
        prevent main window going off screen.

        TODO: Clean up this code as it is long and can most likely be improved.
        """
        win_size = settings.get_window_size()   # QSize()

        # Hide window if visible and leave function
        if self.isVisible():
            # Store window position and size
            settings.set_window_pos(self.pos())
            settings.set_window_size(self.size())

            self.hide()
        else:
            # Desktop number based on cursor
            desktop = QtGui.QDesktopWidget()
            current_screen = desktop.screenNumber(QtGui.QCursor().pos())
            logging.debug('Screen #=%s' % current_screen)

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
            logging.debug('GlobalScreenRect=(%d,%d,%d,%d)' % (x_min, y_min,
                                                              x_max, y_max))

            # 2: System tray
            if settings.get_open_window_at() == 2:
                x = self.tray_icon.geometry().x()
                y = self.tray_icon.geometry().y()
                logging.debug('SystemTrayCoords=(%d,%d)' % (x, y))

            # 1: Last position
            elif settings.get_open_window_at() == 1:
                x = settings.get_window_pos().x()
                y = settings.get_window_pos().y()
                logging.debug('LastPositionCoords=(%d,%d)' % (x ,y))

            # 0: At mouse cursor
            else:
                x = QtGui.QCursor().pos().x()
                y = QtGui.QCursor().pos().y()
                logging.debug('CursorCoords=(%d,%d)' % (x, y))

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

            logging.debug('MainWindowCoords=(%d,%d)' % (x, y))
            logging.debug('MainWindowSize=(%d,%d)' % (win_size.width(), 
                                                      win_size.height()))

            # Reposition and resize the main window
            self.move(x, y)
            self.resize(win_size.width(), win_size.height())

            self.show()             # Open window
            self.activateWindow()   # Bring to front
            self.main_widget.check_selection()

    def _set_hot_key(self):
        """Helper function to bind global hot key to OS specific binder class.

        If binding fails then display a message in system tray notification 
        tray.
        """
        hotkey = settings.get_global_hot_key()  # <CTRL><ALT>H
        if not self.key_binder.bind(hotkey, self._on_toggle_window):
            title = 'Global Hot Key'
            message = 'Failed to bind global hot key %s.' % hotkey
            self.tray_icon.showMessage(title, message, 
                                       icon=QtGui.QSystemTrayIcon.Warning,
                                       msecs=10000)


class MainWidget(QtGui.QWidget):
    """Main widget container for main window.
    """
    def __init__(self, parent=None):        
        super(MainWidget, self).__init__(parent)
        self.parent = parent

        # Ignore clipboard change when user sets item to clipboard
        self.ignore_created = False

        # Monitor clipboards
        self.clipboard_monitor = clipboards.ClipBoards(self)

        # Create view, model, and proxy
        self.view_main = view.ListView(self)
        self.model_main = model.MainSqlTableModel(self)
        
        self.proxy_main = searchbox.SearchFilterProxyModel(self)
        self.proxy_main.setSourceModel(self.model_main)

        # self.proxy_main = QtGui.QSortFilterProxyModel(self)
        # self.proxy_main.setFilterKeyColumn(TITLEFULL)
        # self.proxy_main.setSourceModel(self.model_main)
        # self.proxy_main.setDynamicSortFilter(True)
        # self.proxy_main.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.view_main.setModel(self.proxy_main)
        self.view_main.setModelColumn(TITLESHORT)
        
        # Pass view and proxy pointers to search box class
        self.search_box = searchbox.SearchBox(self.view_main, self.proxy_main)

        settings_button = QtGui.QPushButton(self)
        settings_button.setIcon(QtGui.QIcon.fromTheme('emblem-system', 
                                QtGui.QIcon(
                                  utils.resource_filename('icons/settings.png')
                                )))
        settings_button.setToolTip('Settings...')

        # Create layout
        layout = QtGui.QGridLayout(self)
        layout.addWidget(self.search_box, 0, 0)
        layout.addWidget(settings_button, 0, 1)
        layout.addWidget(self.view_main, 1, 0, 1, 2)
        self.setLayout(layout)

        # Set clipboard contents if return pressed or from right click menu
        self.connect(self.search_box, QtCore.SIGNAL('returnPressed()'), 
                     self.on_set_clipboard)
        
        # Search proxy model
        self.connect(self.search_box, QtCore.SIGNAL('textChanged(QString)'), 
                     self.proxy_main.setFilterFixedString)

        # Check selection in view during search
        self.connect(self.search_box, QtCore.SIGNAL('textChanged(QString)'), 
                     self.check_selection)

        # Set clipboard data from signal by view
        self.connect(self.view_main, QtCore.SIGNAL('set-clipboard()'), 
                     self.on_set_clipboard)

        # Open settings dialog from button next to search box
        self.connect(settings_button, QtCore.SIGNAL('clicked()'), 
                     self._emit_open_settings)

        # Open settings dialog from right click menu of the view
        self.connect(self.view_main, QtCore.SIGNAL('open-settings()'),
                     self._emit_open_settings)

        # Show preview of selected item in view
        self.connect(self.view_main,
                     QtCore.SIGNAL('open-preview(QModelIndex)'), 
                     self._on_open_preview)

        # Clipboard dataChanged() emits to append new item to model->view
        self.connect(self.clipboard_monitor,
                     QtCore.SIGNAL('new-item(QMimeData)'), self._on_new_item)

    @QtCore.Slot(str)
    def check_selection(self, text=None):
        """Prevents selection from disappearing during proxy filter.

        Args:
            text (str): Ignored parameter as the signal emits it.
        """
        selection_model = self.view_main.selectionModel()
        indexes = selection_model.selectedIndexes()

        if not indexes:
            index = self.proxy_main.index(0, TITLESHORT)
            selection_model.select(index, QtGui.QItemSelectionModel.Select)
            selection_model.setCurrentIndex(index, 
                                            QtGui.QItemSelectionModel.Select)

    @QtCore.Slot()
    def _emit_open_settings(self):
        """Emit signal to open settings dialog.
        """
        self.emit(QtCore.SIGNAL('open-settings()'))

    def _duplicate(self, checksum):
        """Checks for a duplicate row in Main table.

        Searches entire model for a duplicate checksum on new item that 
        requested to be created. If duplicate is found then update the source 
        DATE column and submit changes. 

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

            # Update DATE column if checksums match
            if str(checksum) == str(checksum_source):
                logging.debug('%s == %s' % (checksum, checksum_source))
                
                self.model_main.setData(self.model_main.index(row, DATE), 
                                    QtCore.QDateTime.currentMSecsSinceEpoch())
                self.model_main.submit()
                logging.info(True)
                return True
                
        logging.info(False)

        return False

    @QtCore.Slot(QtCore.QMimeData)
    def _on_new_item(self, mime_data):
        """Append new clipboard contents to database.

        Performs checksum for new data vs database. If duplicate found, then 
        the time is updated in a seperate function. Once parent data is 
        created, the mime data is converted to QByteArray and stored in data 
        table as a blob.

        Args:
            mime_data (QMimeData): clipboard contents mime data

        Returns: 
            True (bool): Successfully added data to model.
            None: User just set new clipboard data trigger dataChanged() to be
                emited. Data does not have any text. Duplicate found. Storing 
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
        # TODO: Make class that handles platform dependency
        if sys.platform.startswith('win32'):
            proc_name = clipboards.get_win32_owner()
        elif sys.platform.startswith('linux'):
            proc_name = clipboards.get_x11_owner()
        else:
            proc_name = None

        # Make user entered apps lowercase and into a list
        if proc_name is not None:
            ignore_list = settings.get_exclude().lower().split(';')
            if proc_name.lower() in ignore_list:
                logging.info('Ignoring clipboard change by %s.' % proc_name)
                return None

        logging.debug('Clipboard Formats: %s' % str(mime_data.formats()))

        checksum = utils.calculate_checksum(mime_data)
        if checksum == None:
            return None
        elif self._duplicate(checksum): # If duplicate found then exit function
            return None

        text = utils.create_full_title(mime_data)

        # title_short used in list row view so clean it up by removing white
        # space, dedent, and striping uncessary line breaks
        title_short = utils.clean_up_text(text)
        title_short = utils.remove_extra_lines(text=title_short,
                                    line_count=settings.get_lines_to_display())

        date = QtCore.QDateTime.currentMSecsSinceEpoch()

        parent_id = database.insert_main(date=date, 
                                         titleshort=title_short,
                                         titlefull=text,
                                         checksum=checksum)

        # Store mime data into database
        if not parent_id:
            logging.error('Failed to create entry in database.')
            return None

        # Highlight top item and then insert mime data
        self.model_main.select() # Update view
        index = QtCore.QModelIndex(self.view_main.model().index(0, TITLESHORT))
        self.view_main.setCurrentIndex(index)

        # Convert mime data based on format to ByteArray
        data_insert = []
        for format in MIME_REFERENCES:
            if mime_data.hasFormat(format):
                byte_data = QtCore.QByteArray(mime_data.data(format))
                data_insert.append([format, byte_data])

        for format, __ in data_insert:
            logging.debug('Format Saved: %s' % format)
        
        # Insert mime data into database
        for format, byte_data in data_insert:
            database.insert_mime(parent_id, format, byte_data)

        # Maintain maximum number of entries    
        self._check_max_entries()

        # Check expiration of entries
        if settings.get_expire_value() != 0:
            self._check_expired_entries()

        return True

    def _check_expired_entries(self):
        # Work in reverse and break when row date is less than
        # expiration date
        max_entries = settings.get_max_entries_value()
        entries = range(0, self.model_main.rowCount())
        entries.reverse()   # Start from bottom of QListView

        for row in entries:
            logging.debug('Row: %d' % row)
            index = self.model_main.index(row, DATE)
            date = self.model_main.data(index)
            logging.debug('Date: %s' % date)

            # Convert from ms to s
            time = datetime.datetime.fromtimestamp(date/1000)
            today = datetime.datetime.today()
            delta = today - time
            
            
            logging.debug('Delta: %d days' % delta.days)
            if delta.days > settings.get_expire_value():
                index = self.model_main.index(row, ID)
                parent_id = self.model_main.data(index)

                database.delete_mime(parent_id)
                self.model_main.removeRow(row)
            else:
                logging.debug('Last row not expired, breaking!')
                break

        self.model_main.submitAll()

    def _check_max_entries(self):
        row_count = self.model_main.rowCount()
        max_entries = settings.get_max_entries_value()

        logging.debug('Row count: %s' % row_count)
        logging.debug('Max entries: %s' % max_entries)

        if row_count > max_entries:
            # Delete extra rows
            # self.model_main.removeRows(max_entries, row_count-max_entries)
            for row in range(max_entries, row_count):
                logging.debug('Row: %d' % row)

                index_id = self.model_main.index(row, ID)
                parent_id = self.model_main.data(index_id)

                database.delete_mime(parent_id)
                self.model_main.removeRow(row)

            self.model_main.submitAll()
   
    @QtCore.Slot(QtCore.QModelIndex)
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
        logging.debug('ID: %s' % parent_id)

        # Find all childs relating to parent_id
        mime_list = database.get_mime(parent_id)

        # Create QMimeData object based on formats and byte data
        mime_data = QtCore.QMimeData()
        for format, byte_data in mime_list:
            mime_data.setData(format, byte_data)

        # PreviewDialog(self) so it opens at main window
        preview_dialog = dialogs.PreviewDialog(self)
        preview_dialog.setup_ui(mime_data)
        preview_dialog.exec_()
      
    @QtCore.Slot()
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
        logging.debug('ParentID: %s' % parent_id)

        # Find all childs relating to parent_id
        mime_list = database.get_mime(parent_id)

        # Create QMimeData object based on formats and byte data
        mime_data = QtCore.QMimeData()
        for format, byte_data in mime_list:
            mime_data.setData(format, byte_data)
        
        # Set to clipboard
        self.clipboard_monitor.set_data(mime_data)

        # Send Ctrl+V key stroke (paste) to foreground window
        if settings.get_send_paste():
            paste.send_event()

        # Update the date column in source
        self.model_main.setData(self.model_main.index(model_index.row(), DATE), 
                                QtCore.QDateTime.currentMSecsSinceEpoch())
        self.model_main.submitAll()