#!/usr/bin/env python2

import logging
import optparse
import os
import sys
from logging.handlers import RotatingFileHandler

from PySide.QtCore import QDir, QEvent, SIGNAL, Slot
from PySide.QtGui import QApplication

from clipmanager.defs import APP_DOMAIN, APP_NAME, APP_ORG, APP_VERSION
from clipmanager.singleinstance import SingleInstance
from clipmanager.ui.mainwindow import MainWindow

package = os.path.dirname(os.path.abspath(__file__))
installation_directory = os.path.join(package, '..')
sys.path.insert(0, installation_directory)


def _setup_logger(logging_level='INFO'):
    log_path = os.path.join(QDir.tempPath(), APP_NAME.lower() + '.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logger = logging.getLogger('clipmanager')
    logger.setLevel(logging_level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = RotatingFileHandler(log_path, maxBytes=1048576)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class Application(QApplication):
    """Application event loop which spawns the main window."""

    def __init__(self, args):
        """Initialize application and launch main window.

        :param args: 'minimize' on launch
        :type args: list
        """
        super(Application, self).__init__(args)

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


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', default='INFO',
                      help='Logging level')
    (options, args) = parser.parse_args()

    _setup_logger(options.logging_level)

    single_instance = SingleInstance()
    if not single_instance.is_running():
        app = Application(sys.argv)

        sys.exit(app.exec_())

    sys.exit(-1)
