#!/usr/bin/env python2

import logging
import logging.config
import optparse

from PySide.QtCore import QDir, QEvent, SIGNAL, Slot
from PySide.QtGui import QApplication

from clipmanager.defs import APP_DOMAIN, APP_NAME, APP_ORG, APP_VERSION
from clipmanager.mainwindow import MainWindow
from clipmanager.singleinstance import SingleInstance

LOGGING_LEVELS = {
    'critical': 'CRITICAL',
    'error': 'ERROR',
    'warning': 'WARNING',
    'info': 'INFO',
    'debug': 'DEBUG'
}


def setup_logging(logging_level):
    log_file_path = '%s/%s.log' % (QDir.tempPath(), APP_NAME)
    dict_log_config = {
        'version': 1,
        'handlers': {
            'file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'custom_format',
                'filename': log_file_path,
                'maxBytes': 1048576,
                'backupCount': 0,
            },
            'stream_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'custom_format',
                'stream': 'ext://sys.stdout',
            }
        },
        'loggers': {
            '': {
                'handlers': ['file_handler', 'stream_handler'],
                'level': logging_level,
            }
        },
        'formatters': {
            'custom_format': {
                'format': '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)s - %(message)s'
            }
        }
    }
    logging.config.dictConfig(dict_log_config)


class MainApp(QApplication):
    """Application event loop which spawns the main window."""

    def __init__(self, args):
        """Initialize application properties and open main window.

        :param args: sys.argv
        :type args: list
        """
        super(MainApp, self).__init__(args)

        self.setApplicationName(APP_DOMAIN)
        self.setOrganizationName(APP_ORG)
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)

        # do not exit if main window hidden
        self.setQuitOnLastWindowClosed(False)

        if 'minimize' in args:
            self.mw = MainWindow(minimize=True)
        else:
            self.mw = MainWindow(minimize=False)

        # Perform clean up actions when quit message signaled
        self.connect(self, SIGNAL('aboutToQuit()'), self.quit)

    @Slot()
    def quit(self):
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
        self.mw.destroy()

        # Copy and remove pointer
        clipboard = QApplication.clipboard()
        event = QEvent(QEvent.Clipboard)
        QApplication.sendEvent(clipboard, event)
        logging.info('Exiting...')


def main(argv):
    # Allow user to set a logging level if issues
    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', help='Logging level')
    (options, args) = parser.parse_args()
    logging.debug(options)
    logging.debug(args)

    # If user does not specify an option then lower will fail
    try:
        log_option = options.logging_level.lower()
    except AttributeError:
        log_option = options.logging_level

    logging_level = LOGGING_LEVELS.get(log_option, 'INFO')
    setup_logging(logging_level)

    single_instance = SingleInstance()
    if single_instance.is_running():
        logging.warn('Application already running!')
        return -1

    app = MainApp(argv)
    run = app.exec_()

    logging.info('Exit code: %s' % run)
    return run


if __name__ == '__main__':
    import sys

    sys.exit(main(sys.argv))
