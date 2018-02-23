import os

from PySide.QtGui import QIcon

from clipmanager import resources


def get_icon(name):
    """Helper to load QIcon from theme or QResources.

    :param name: Filename of the icon: search.png.
    :type name: str

    :return: Qt QIcon class.
    :rtype: QIcon
    """
    basename = os.path.splitext(name)[0]

    icon = QIcon.fromTheme(basename)
    if not icon.isNull():
        return icon

    return QIcon(':/icons/{}'.format(name))
