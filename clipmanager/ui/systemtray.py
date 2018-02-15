import logging

from PySide.QtCore import QCoreApplication, SIGNAL, Slot
from PySide.QtGui import QAction, QMenu, QSystemTrayIcon

from clipmanager import __title__
from clipmanager.settings import settings
from clipmanager.ui.dialogs.about import AboutDialog
from clipmanager.ui.icons import get_icon

logger = logging.getLogger(__name__)


class SystemTrayIcon(QSystemTrayIcon):
    """Application system tray icon with right click menu."""

    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)

        self.parent = parent

        self.setIcon(get_icon('clipmanager.ico'))
        self.setToolTip(__title__)

        menu = QMenu(parent)

        toggle_action = QAction(get_icon('search'), '&Toggle', self)
        toggle_action.triggered.connect(self.emit_toggle_window)

        settings_action = QAction(get_icon('preferences-system'),
                                  '&Settings',
                                  self)
        settings_action.triggered.connect(self.emit_open_settings)

        about_action = QAction(get_icon('help-about'), '&About', self)
        about_action.triggered.connect(self.open_about)

        exit_action = QAction(get_icon('application-exit'), '&Quit', self)
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
    def emit_toggle_window(self):
        """Emit signal to toggle the main window.

        :return: None
        :rtype: None
        """
        self.emit(SIGNAL('toggleWindow()'))

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

    @Slot()
    def emit_open_settings(self):
        """Emit signal to open the settings dialog.

        :return: None
        :rtype: None
        """
        self.emit(SIGNAL('openSettings()'))

    @Slot()
    def toggle_private(self):
        """Toggle and save private settings.

        :return: None
        :rtype: None
        """
        settings.set_disconnect(not settings.get_disconnect())
