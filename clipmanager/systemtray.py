#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from PySide import QtCore
from PySide import QtGui

from defs import APP_NAME
from dialogs import AboutDialog
from settings import settings

logging.getLogger(__name__)


def _disconnect_icon():
    """Determine which icon to display if disconnect menu is toggled on/off.

    Returns:
        QtGui.QIcon
    """
    # Clipboard _disconnected and ignoring changes
    if settings.get_disconnect():
        return QtGui.QIcon.fromTheme('network-offline',
               QtGui.QIcon('icons/disconnect.png'))
    # Clipboard connected and monitoring
    else:
        return QtGui.QIcon.fromTheme('network-transmit-receive', 
               QtGui.QIcon('icons/connect.png'))


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    """System tray icon with right click menu and ability to open main window
    by clicking on the icon.
    """
    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        self.parent = parent

        self.setIcon(QtGui.QIcon('icons/app.ico'))
        self.setToolTip(APP_NAME)
        self.setup_menu()

    def setup_menu(self):
        """Create right click menu.
        """
        # Right click menu
        menu = QtGui.QMenu()

        # Open or hide main window
        toggle_act = menu.addAction(QtGui.QIcon.fromTheme('search', 
                                    QtGui.QIcon('icons/search.png')), 'Toggle')

        menu.addSeparator()

        # Disconnect from OS clipboard(s)
        self.disconnect_act = menu.addAction(_disconnect_icon(), 'Disconnect')
        self.disconnect_act.setCheckable(True)
        self.disconnect_act.setChecked(settings.get_disconnect())

        # Open settings dialog
        settings_act = menu.addAction(QtGui.QIcon.fromTheme('emblem-system', 
                                      QtGui.QIcon('icons/settings.png')), 
                                      'Settings')

        # Open about dialog
        about_act = menu.addAction(QtGui.QIcon.fromTheme('help-about', 
                                   QtGui.QIcon('icons/about.png')), 'About')

        menu.addSeparator()

        # Exit application
        exit_act = menu.addAction(QtGui.QIcon.fromTheme('application-exit', 
                                  QtGui.QIcon('icons/exit.png')), 'Quit')

        # Connect menu triggered action to functions
        self.connect(toggle_act, QtCore.SIGNAL('triggered()'), 
                     self._emit_toggle_window)
        self.connect(self.disconnect_act, QtCore.SIGNAL('triggered()'), 
                     self._disconnect)
        self.connect(settings_act, QtCore.SIGNAL('triggered()'), 
                     self._emit_open_settings)
        self.connect(about_act, QtCore.SIGNAL("triggered()"), self._about)
        self.connect(exit_act, QtCore.SIGNAL("triggered()"), self._exit)

        self.setContextMenu(menu)

    def _emit_toggle_window(self):
        """Emit signal to toggle the main window.
        """
        self.emit(QtCore.SIGNAL('toggle-window()'))

    def _emit_open_settings(self):
        """Emit signal to open the settings dialog.
        """
        self.emit(QtCore.SIGNAL('open-settings()'))

    def _disconnect(self):
        """Save and change icon for disconnecting from clipboard.
        """
        settings.set_disconnect(not settings.get_disconnect())
        self.disconnect_act.setIcon(_disconnect_icon())

    def _about(self):
        """Open about dialog.
        """
        about = AboutDialog(self.parent)    # Opens dialog near main window
        about.exec_()
        del about
        
    def _exit(self):
        """Tell the application to exit with return code 0 (success).
        """
        QtCore.QCoreApplication.quit()


