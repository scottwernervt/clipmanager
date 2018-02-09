import logging

from PySide.QtCore import QCoreApplication, SIGNAL
from PySide.QtGui import QIcon, QMenu, QSystemTrayIcon

from clipmanager.defs import APP_NAME
from clipmanager.settings import settings
from clipmanager.ui.dialogs.about import AboutDialog
from clipmanager.utils import resource_filename

logger = logging.getLogger(__name__)


def _load_disconnect_icon():
    """Load disconnect icon if menu item is checked or unchecked.

    :return: Icon.
    :rtype: QIcon
    """
    if settings.get_disconnect():
        theme = ('network-offline',
                 QIcon(resource_filename('icons/disconnect.png')))
    else:
        theme = ('network-transmit-receive',
                 QIcon(resource_filename('icons/connect.png')))

    return QIcon.fromTheme(*theme)


class SystemTrayIcon(QSystemTrayIcon):
    """Application system tray icon with right click menu."""

    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)

        self.parent = parent

        self.setIcon(QIcon(resource_filename('icons/clipmanager.ico')))
        self.setToolTip(APP_NAME)
        self.setup_menu()

    def setup_menu(self):
        """Create right click menu.

        :return: None
        :rtype: None
        """
        menu = QMenu()

        toggle_window_action = menu.addAction(
            QIcon.fromTheme(
                'search',
                QIcon(resource_filename('icons/search.png'))
            ),
            'Toggle'
        )

        menu.addSeparator()

        self.disconnect_action = menu.addAction(_load_disconnect_icon(),
                                                'Disconnect')
        self.disconnect_action.setCheckable(True)
        self.disconnect_action.setChecked(settings.get_disconnect())

        settings_action = menu.addAction(
            QIcon.fromTheme(
                'emblem-system',
                QIcon(resource_filename('icons/settings.png'))
            ),
            'Settings'
        )

        about_action = menu.addAction(
            QIcon.fromTheme(
                'help-about',
                QIcon(resource_filename('icons/about.png'))
            ),
            'About'
        )

        menu.addSeparator()

        exit_action = menu.addAction(
            QIcon.fromTheme(
                'application-exit',
                QIcon(resource_filename('icons/exit.png'))
            ),
            'Quit'
        )

        self.connect(toggle_window_action, SIGNAL('triggered()'),
                     self._emit_toggle_window)
        self.connect(self.disconnect_action, SIGNAL('triggered()'),
                     self._disconnect)
        self.connect(settings_action, SIGNAL('triggered()'),
                     self._emit_open_settings)
        self.connect(about_action, SIGNAL("triggered()"), self._about)
        self.connect(exit_action, SIGNAL("triggered()"), self._exit)

        self.setContextMenu(menu)

    def _emit_toggle_window(self):
        """Emit signal to toggle the main window.

        :return: None
        :rtype: None
        """
        self.emit(SIGNAL('toggleWindow()'))

    def _emit_open_settings(self):
        """Emit signal to open the settings dialog.

        :return: None
        :rtype: None
        """
        self.emit(SIGNAL('openSettings()'))

    def _disconnect(self):
        """Toggle and save disconnect settings.

        :return: None
        :rtype: None
        """
        settings.set_disconnect(not settings.get_disconnect())
        self.disconnect_action.setIcon(_load_disconnect_icon())

    def _about(self):
        """Open about dialog.

        :return: None
        :rtype: None
        """
        # parent forces dialog to load near main window
        about = AboutDialog(self.parent)
        about.exec_()
        del about

    def _exit(self):
        """Exit application.

        :return: None
        :rtype: None
        """
        QCoreApplication.quit()
