import logging

from PySide.QtCore import QCoreApplication, Signal, Slot
from PySide.QtGui import QAction, QMenu, QSystemTrayIcon

from clipmanager import __title__
from clipmanager.settings import Settings
from clipmanager.ui.dialogs.about import AboutDialog
from clipmanager.ui.icons import get_icon

logger = logging.getLogger(__name__)


class SystemTrayIcon(QSystemTrayIcon):
    """Application system tray icon with right click menu."""
    toggle_window = Signal()
    open_settings = Signal()

    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)

        self.parent = parent

        self.setToolTip(__title__)
        self.setIcon(get_icon('clipmanager.ico'))

        self.settings = Settings()

        menu = QMenu(parent)

        toggle_action = QAction('&Toggle', self)
        toggle_action.triggered.connect(self.emit_toggle_window)

        settings_action = QAction(get_icon('preferences-system.png'),
                                  '&Settings',
                                  self)
        settings_action.triggered.connect(self.emit_open_settings)

        about_action = QAction(get_icon('help-about.png'), '&About', self)
        about_action.triggered.connect(self.open_about)

        exit_action = QAction(get_icon('application-exit.png'), '&Quit', self)
        exit_action.triggered.connect(QCoreApplication.quit)

        disconnect_action = QAction('&Private mode', self)
        disconnect_action.setCheckable(True)
        disconnect_action.setChecked(self.settings.get_disconnect())
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
    def toggle_private(self):
        """Toggle and save private self.settings.

        :return: None
        :rtype: None
        """
        self.settings.set_disconnect(not self.settings.get_disconnect())

    @Slot()
    def open_about(self):
        """Open about dialog.

        :return: None
        :rtype: None
        """
        about = AboutDialog()
        about.exec_()
        del about

    @Slot()
    def emit_toggle_window(self):
        """Emit signal to toggle the main window.

        :return: None
        :rtype: None
        """
        self.toggle_window.emit()

    @Slot()
    def emit_open_settings(self):
        """Emit signal to open the settings dialog.

        :return: None
        :rtype: None
        """
        self.open_settings.emit()
