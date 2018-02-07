import logging

from PySide.QtCore import QCoreApplication, SIGNAL
from PySide.QtGui import QIcon, QMenu, QSystemTrayIcon

from clipmanager.defs import APP_NAME
from clipmanager.dialogs import AboutDialog
from clipmanager.settings import settings
from clipmanager.utils import resource_filename

logger = logging.getLogger(__name__)


def _disconnect_icon():
    """Determine which icon to display if disconnect menu is toggled on/off.

    Returns:
        QIcon
    """
    # Clipboard _disconnected and ignoring changes
    if settings.get_disconnect():
        return QIcon.fromTheme('network-offline',
                               QIcon(resource_filename(
                                   'icons/disconnect.png')))
    # Clipboard connected and monitoring
    else:
        return QIcon.fromTheme('network-transmit-receive',
                               QIcon(resource_filename(
                                   'icons/connect.png')))


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon with right click menu and ability to open main window
    by clicking on the icon.
    """

    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        self.parent = parent

        self.setIcon(QIcon(resource_filename('icons/clipmanager.ico')))
        self.setToolTip(APP_NAME)
        self.setup_menu()

    def setup_menu(self):
        """Create right click menu.
        """
        # Right click menu
        menu = QMenu()

        # Open or hide main window
        toggle_act = menu.addAction(QIcon.fromTheme('search',
                                                    QIcon(
                                                        resource_filename(
                                                            'icons/search.png'))),
                                    'Toggle')

        menu.addSeparator()

        # Disconnect from OS clipboard(s)
        self.disconnect_act = menu.addAction(_disconnect_icon(), 'Disconnect')
        self.disconnect_act.setCheckable(True)
        self.disconnect_act.setChecked(settings.get_disconnect())

        # Open settings dialog
        settings_act = menu.addAction(QIcon.fromTheme('emblem-system',
                                                      QIcon(
                                                          resource_filename(
                                                              'icons/settings.png'))),
                                      'Settings')

        # Open about dialog
        about_act = menu.addAction(QIcon.fromTheme('help-about',
                                                   QIcon(
                                                       resource_filename(
                                                           'icons/about.png'))),
                                   'About')

        menu.addSeparator()

        # Exit application
        exit_act = menu.addAction(QIcon.fromTheme('application-exit',
                                                  QIcon(
                                                      resource_filename(
                                                          'icons/exit.png'))),
                                  'Quit')

        # Connect menu triggered action to functions
        self.connect(toggle_act, SIGNAL('triggered()'),
                     self._emit_toggle_window)
        self.connect(self.disconnect_act, SIGNAL('triggered()'),
                     self._disconnect)
        self.connect(settings_act, SIGNAL('triggered()'),
                     self._emit_open_settings)
        self.connect(about_act, SIGNAL("triggered()"), self._about)
        self.connect(exit_act, SIGNAL("triggered()"), self._exit)

        self.setContextMenu(menu)

    def _emit_toggle_window(self):
        """Emit signal to toggle the main window.
        """
        self.emit(SIGNAL('toggleWindow()'))

    def _emit_open_settings(self):
        """Emit signal to open the settings dialog.
        """
        self.emit(SIGNAL('openSettings()'))

    def _disconnect(self):
        """Save and change icon for disconnecting from clipboard.
        """
        settings.set_disconnect(not settings.get_disconnect())
        self.disconnect_act.setIcon(_disconnect_icon())

    def _about(self):
        """Open about dialog.
        """
        about = AboutDialog(self.parent)  # Opens dialog near main window
        about.exec_()
        del about

    def _exit(self):
        """Tell the application to exit with return code 0 (success).
        """
        QCoreApplication.quit()
