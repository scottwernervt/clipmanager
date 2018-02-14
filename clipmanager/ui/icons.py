import os
import sys

import pkg_resources
from PySide.QtGui import QIcon


def resource(filename):
    """Load resource from resource package.

    :param filename: File name of resource, e.g. icons\app.ico.
    :type filename: str

    :return: Absolute path to resource file found locally on disk OR a true
        filesystem path for specified resource.
    :rtype: str
    """
    paths = map(lambda p: os.path.join(p, filename),
                (os.path.dirname(sys.argv[0]),),  # windows executable path
                )
    for path in paths:
        if os.path.isfile(path):
            return path

    return pkg_resources.resource_filename('clipmanager', filename)


TOGGLE = QIcon.fromTheme('search', resource('search.png'))
SETTINGS = QIcon.fromTheme('preferences-system',
                           resource('preferences-system.png'))
ABOUT = QIcon.fromTheme('help-about', resource('help-about.png'))
EXIT = QIcon.fromTheme('application-exit',
                       resource('application-exit.png'))

EDIT_PASTE = QIcon.fromTheme('edit-paste', resource('edit-paste.png'))
LIST_REMOVE = QIcon.fromTheme('list-remove',
                              resource('list-remove.png'))
PREVIEW = QIcon.fromTheme('document-print-preview',
                          resource('document-print-preview.png'))
