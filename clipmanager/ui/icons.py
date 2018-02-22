import os

import pkg_resources
from PySide.QtGui import QIcon


def get_icon(name):
    """Helper to load icon from linux theme or fail back to icons folder.

    :param name: Filename of the icon, e.g. search or app.ico.
    :type name: str

    :return: Qt QIcon class.
    :rtype: QIcon
    """
    if not name:
        return QIcon()

    if os.path.isabs(name):
        return QIcon(name)

    icon = QIcon.fromTheme(name)
    if not icon.isNull():
        return icon

    for i in pkg_resources.resource_listdir('clipmanager', 'icons'):
        if i.startswith(name):
            path = pkg_resources.resource_filename('clipmanager',
                                                   os.path.join('icons/', name))
            return QIcon(path)

    return QIcon()
