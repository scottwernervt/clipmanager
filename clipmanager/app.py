#!/usr/bin/env python2

import logging
import logging.config
import optparse

from PySide.QtCore import QDir, QEvent, SIGNAL, Slot
from PySide.QtGui import QApplication

from clipmanager.defs import APP_DOMAIN, APP_NAME, APP_ORG, APP_VERSION
from clipmanager.mainwindow import MainWindow
from clipmanager.singleinstance import SingleInstance


def setup_logging(logging_level):
    log_file_path = '%s/%s.log' % (QDir.tempPath(), APP_NAME.lower())
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
                'format': '%(asctime)s - %(levelname)s - %(module)s.%('
                          'funcName)s:%(lineno)s - %(message)s '
            }
        }
    }
    logging.config.dictConfig(dict_log_config)


class MainApp(QApplication):
    """Application event loop which spawns the main window."""

    def __init__(self, args):
        """Initialize application and launch main window.

        :param args: 'minimize' on launch
        :type args: list
        """
        super(MainApp, self).__init__(args)

        self.setApplicationName(APP_DOMAIN)
        self.setOrganizationName(APP_ORG)
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)

        # prevent application from exiting if minimized "closed"
        self.setQuitOnLastWindowClosed(False)

        if 'minimize' in args:
            self.mw = MainWindow(minimize=True)
        else:
            self.mw = MainWindow(minimize=False)

        self.connect(self, SIGNAL('aboutToQuit()'), self.about_to_quit)

    @Slot()
    def about_to_quit(self):
        """Clean up and set clipboard contents to OS clipboard.

        The basic concept behind this is that by default copying something
        into the clipboard only copies a reference/pointer to the source
        application. Then when another application wants to paste the data
        from the clipboard it requests the data from the source application.

        :return: None
        :rtype: None
        """
        clipboard = QApplication.clipboard()
        event = QEvent(QEvent.Clipboard)
        QApplication.sendEvent(clipboard, event)

        self.mw.destroy()


def main(argv):
    """Entry point for launching ClipManager.

    :param argv:
    :type argv:

    :return:
    :rtype:
    """
    # Allow user to set a logging level if issues
    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', help='Logging level')
    (options, args) = parser.parse_args()

    if options.logging_level:
        logging_level = options.logging_level.upper()
    else:
        logging_level = 'INFO'

    setup_logging(logging_level)

    single_instance = SingleInstance()
    if single_instance.is_running():
        return -1

    app = MainApp(argv)
    app.exec_()


if __name__ == '__main__':
    import sys

    sys.exit(main(sys.argv))
