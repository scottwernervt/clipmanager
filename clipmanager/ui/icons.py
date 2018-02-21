import os
import sys

from PySide.QtGui import QIcon

# windows executable path
app_path = os.path.dirname(os.path.join(sys.argv[0]))
icons_path = os.path.join(app_path, 'icons')
print('app_path', app_path)
print('icons_path', icons_path)


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

    if os.path.exists(icons_path):  # icons folder does not exist for pytest
        for i in os.listdir(icons_path)[::-1]:
            if i.startswith(name):
                path = os.path.join(icons_path, i)
                return QIcon(path)

    return QIcon()
