import os

from PySide.QtCore import QCoreApplication, QDir, QFile
from PySide.QtGui import QDesktopServices

from clipmanager import __version__

APP_ORG = 'Werner'
APP_NAME = 'ClipManager'
APP_DOMAIN = 'https://github.com/scottwernervt/clipmanager/'
APP_VERSION = __version__
APP_AUTHOR = 'Scott Werner'
APP_EMAIL = 'scott.werner.vt@gmail.com'
APP_DESCRIPTION = """Manage the system's clipboard history."""

QCoreApplication.setOrganizationName(APP_ORG)
QCoreApplication.setApplicationName(APP_NAME)
QCoreApplication.setApplicationVersion(APP_VERSION)
QCoreApplication.setOrganizationDomain(APP_DOMAIN)

# Create storage directory based on OS
# Windows
#   XP: C:\Documents and Settings\<username>\Local Settings\Application Data\
#   7/8: C:\Users\<username>\AppData\Local\Werner\ClipManager
# Linux: /home/<username>/.local/share/data/Werner/ClipManager
STORAGE_PATH = QDesktopServices.storageLocation(QDesktopServices.DataLocation)
if not STORAGE_PATH:
    STORAGE_PATH = QDir.homePath() + '/.' + QCoreApplication.applicationName()

if not QFile.exists(STORAGE_PATH):
    directory = QDir()
    directory.mkpath(STORAGE_PATH)

# Database columns set as integers
ID, TITLE, TITLE_SHORT, CHECKSUM, KEEP, CREATED_AT = range(6)
ID, PARENT_ID, MIME_FORMAT, DATA = range(4)

# Formats to check and save with from OS clipboard
MIME_REFERENCES = [
    'text/html',
    'text/html;charset=utf-8',
    'text/plain',
    'text/plain;charset=utf-8',
    'text/richtext',
    'application/x-qt-windows-mime;value="Rich Text Format"',
    'text/uri-list',
    # 'application/x-qt-image'
]

if os.name == 'posix':
    MIME_REFERENCES.extend(['x-special/gnome-copied-files'])
