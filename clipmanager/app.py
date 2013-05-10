#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config
import optparse

from PySide import QtCore
from PySide import QtGui

from defs import APP_DOMAIN
from defs import APP_ORG
from defs import APP_NAME
from defs import APP_VERSION
from mainwindow import MainWindow
from singleinstance import single_instance


LOGGING_LEVELS = {'critical': 'CRITICAL',
                  'error': 'ERROR',
                  'warning': 'WARNING',
                  'info': 'INFO',
                  'debug': 'DEBUG'}


def setup_logging(logging_level):
    log_file_path = '%s/%s%s.log' % (QtCore.QDir.tempPath(), APP_ORG, APP_NAME)
    dict_log_config = {
        'version': 1,
        'handlers': {
            'file_handler': {
                    'class':        'logging.handlers.RotatingFileHandler',
                    'formatter':    'custom_format',
                    'filename':     log_file_path,
                    'maxBytes':     1048576,
                    'backupCount':  0,
            },
            'stream_handler': {
                    'class':        'logging.StreamHandler',
                    'formatter':    'custom_format',
                    'stream':       'ext://sys.stdout',
            }
        },     
        'loggers': {
            '': {
                    'handlers': ['file_handler', 'stream_handler'],
                    'level':    logging_level, # INFO/DEBUG
                }
        },
        'formatters': {
            'custom_format': {
                  'format': '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)s - %(message)s'
            }
        }
    }
    
    logging.config.dictConfig(dict_log_config)
    logging.info(log_file_path)


class MainApp(QtGui.QApplication):
    """Application event loop thats spawns the main window.
    """
    def __init__(self, args):        
        super(MainApp, self).__init__(args)
        """Initialize application properties and open main window.

        Args:
            args (list): sys.argv
        """
        # Prevent a dialog from exiting if main window not visisble
        self.setQuitOnLastWindowClosed(False) 

        # Set application properties
        self.setApplicationName(APP_DOMAIN)
        self.setOrganizationName(APP_ORG)
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)

        # Crebate main window
        self.mw = MainWindow()

        # Perform clean up actions when quit message signaled
        self.connect(self, QtCore.SIGNAL('aboutToQuit()'), self._on_quit)

    @QtCore.Slot()
    def _on_quit(self):
        """Cleanup application and copy clipboard data to OS clipboard.

        Makes a copy of the clipboard pointer data into the OS clipboard. The 
        basic concept behind this is that by default copying something into the
        clipboard only copies a reference/pointer to the source application. 
        Then when another application wants to paste the data from the 
        clipboard  it requests the data from the source application.

        Args:
            None

        Returns:
            None
        """
        self.mw.clean_up()

        # Copy and remove pointer
        clipboard = QtGui.QApplication.clipboard()
        event = QtCore.QEvent(QtCore.QEvent.Clipboard)
        QtGui.QApplication.sendEvent(clipboard, event)
        logging.debug('Exiting...')


def main(argv):
    # Allow user to set a logging level if issues
    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', help='Logging level')
    (options, args) = parser.parse_args()

    # If user does not specify an option then lower will fail
    try:
        log_option = options.logging_level.lower()
    except AttributeError:
        log_option = options.logging_level

    logging_level = LOGGING_LEVELS.get(log_option, 'INFO')
    setup_logging(logging_level)

    if single_instance.already_running():
        logging.warn('Application already running!')
        return -1

    app = MainApp(argv)
    run = app.exec_()

    logging.debug('Exit code: %s' % run)
    return run


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))