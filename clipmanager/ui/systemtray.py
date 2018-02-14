import logging

from PySide.QtCore import QCoreApplication, SIGNAL, Slot
from PySide.QtGui import QAction, QIcon, QMenu, QSystemTrayIcon

from clipmanager.defs import APP_NAME
from clipmanager.settings import settings
from clipmanager.ui import icons
from clipmanager.ui.dialogs.about import AboutDialog
from clipmanager.ui.icons import resource

logger = logging.getLogger(__name__)


class SystemTrayIcon(QSystemTrayIcon):
    """Application system tray icon with right click menu."""

    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)

        self.parent = parent

        self.setIcon(QIcon(resource('icons/clipmanager.ico')))
        self.setToolTip(APP_NAME)

        menu = QMenu()

        toggle_action = QAction(icons.TOGGLE, '&Toggle', self)
        toggle_action.triggered.connect(self.toggle_window)

        settings_action = QAction(icons.SETTINGS, '&Settings', self)
        settings_action.triggered.connect(self.open_settings)

        about_action = QAction(icons.ABOUT, '&About', self)
        about_action.triggered.connect(self.open_about)

        exit_action = QAction(icons.EXIT, '&Quit', self)
        exit_action.triggered.connect(QCoreApplication.quit)

        disconnect_action = QAction('&Private mode', self)
        disconnect_action.setCheckable(True)
        disconnect_action.setChecked(settings.get_disconnect())
        disconnect_action.triggered.connect(self.toggle_private)

        menu.addAction(toggle_action)
        menu.addSeparator()
        menu.addAction(disconnect_action)
        menu.addAction(settings_action)
        menu.addAction(about_action)
        menu.addSeparator()
        menu.addAction(exit_action)

        self.setContextMenu(menu)

    @Slot()
    def toggle_window(self):
        """Emit signal to toggle the main window.

        :return: None
        :rtype: None
        """
        self.emit(SIGNAL('toggleWindow()'))

    @Slot()
    def toggle_private(self):
        """Toggle and save disconnect settings.

        :return: None
        :rtype: None
        """
        settings.set_disconnect(not settings.get_disconnect())
        # self.contextMenu().menuAction().setIcon(_disconnect_icon())

    @Slot()
    def open_settings(self):
        """Emit signal to open the settings dialog.

        :return: None
        :rtype: None
        """
        self.emit(SIGNAL('openSettings()'))

    @Slot()
    def open_about(self):
        """Open about dialog.

        :return: None
        :rtype: None
        """
        # parent forces dialog to load near main window
        about = AboutDialog(self.parent)
        about.exec_()
        del about
