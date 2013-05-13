#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PySide import QtCore
from PySide import QtGui

from __init__ import __version__


APP_ORG = 'Werner'
APP_NAME = 'ClipManager'
APP_DOMAIN = 'https://bitbucket.org/mercnet/clipmanager'
APP_VERSION = __version__
APP_AUTHOR = 'Scott Werner'
APP_DESCRIPTION = """Manage the system's clipboard history."""

QtCore.QCoreApplication.setOrganizationName(APP_ORG)
QtCore.QCoreApplication.setApplicationName(APP_NAME)
QtCore.QCoreApplication.setApplicationVersion(APP_VERSION)
QtCore.QCoreApplication.setOrganizationDomain(APP_DOMAIN)

# Create storage directory based on OS
# Windows
#   XP: C:\Documents and Settings\<username>\Local Settings\Application Data\
#   7/8: C:\Users\<username>\AppData\Local\Werner\ClipManager
# Linux: /home/<username>/.local/share/data/Werner/ClipManager
STORAGE_PATH = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation)
if not STORAGE_PATH:
    STORAGE_PATH = QtCore.QDir.homePath() + '/.' + QtCore.QCoreApplication.applicationName()
if not QtCore.QFile.exists(STORAGE_PATH):
    directory = QtCore.QDir()
    directory.mkpath(STORAGE_PATH)

# Database columns set as integers
ID, DATE, TITLESHORT, TITLEFULL, CHECKSUM = range(5)
ID, PARENTID, FORMAT, DATA = range(4)

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

if sys.platform.startswith('linux'):
    MIME_REFERENCES.extend(['x-special/gnome-copied-files'])