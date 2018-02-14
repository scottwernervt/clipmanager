import os
import sys

import pkg_resources
from PySide.QtGui import QIcon


def get_resource(filename):
    """Load get_resource from get_resource package.

    :param filename: File name of get_resource, e.g. icons\app.ico.
    :type filename: str

    :return: Absolute path to get_resource file found locally on disk OR a true
        filesystem path for specified get_resource.
    :rtype: str
    """
    paths = map(lambda p: os.path.join(p, filename),
                (os.path.dirname(sys.argv[0]),),  # windows executable path
                )
    for path in paths:
        if os.path.isfile(path):
            return path

    return pkg_resources.resource_filename('clipmanager', filename)


SETTINGS = QIcon.fromTheme('preferences-system')
ABOUT = QIcon.fromTheme('help-about')
EXIT = QIcon.fromTheme('application-exit')

EDIT_PASTE = QIcon.fromTheme('edit-paste')
LIST_REMOVE = QIcon.fromTheme('list-remove')
PREVIEW = QIcon.fromTheme('document-print-preview')
