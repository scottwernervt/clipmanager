#!/usr/bin/env python
# https://github.com/CorundumGames/Invasodado/blob/master/setup.py

import glob
import os
import sys

from cx_Freeze import Executable, setup

from clipmanager import __author__, __description__, __title__, __version__

# Working directory
pwd = os.path.dirname(sys.argv[0])

# Executable script
script = os.path.join(pwd, 'bin', 'clipmanager')

# Python installation path for copying Qt drivers and plugins
py_install_path, __ = os.path.split(sys.executable)
packages_path = os.path.join(py_install_path, 'lib', 'site-packages')

# Path to icons/images
icons_path = os.path.join(pwd, 'clipmanager', 'icons', '*.*')  # Glob
icon = os.path.join(pwd, 'clipmanager', 'icons', 'clipmanager.ico')

# Python packages
includes = [
    'ctypes',
    'logging',
    'os',
    'pkg_resources',
    'textwrap',
    're',
    'subprocess',
    'sys',
    'zlib',
]

# 3rd Party Python Packages
includes.extend([
    'PySide.QtCore',
    'PySide.QtGui',
    'PySide.QtSql',
    'PySide.QtNetwork',
    'PySide.QtWebKit',
])

# Packages
packages = ['clipmanager']

# Packages to exclude
excludes = ['email', 'json', 'unittest', 'xml']

# Include files like images, data, etc
include_files = []
for file_path in glob.glob(icons_path):
    path, filename = os.path.split(file_path)
    include_files.append((file_path, os.path.join('icons', filename)))

# Platform dependent packages and settings
if sys.platform.startswith('win32'):
    base = 'Win32GUI'
    target_name = __title__.lower() + '.exe'

    # Window api packages
    includes.extend(['win32event', 'win32process', 'win32api', 'winerror'])
    include_files.extend([
        (
            os.path.join(packages_path, 'PySide', 'plugins', 'imageformats',
                         'qico4.dll'),
            os.path.join('imageformats', 'qico4.dll')
        ),
        (
            os.path.join(packages_path, 'PySide', 'plugins', 'sqldrivers',
                         'qsqlite4.dll'),
            os.path.join('sqldrivers', 'qsqlite4.dll')
        )
    ])
elif sys.platform.startswith('linux'):
    base = 'Console'
    target_name = __title__.lower()
    includes.extend(['subprocess'])

target = Executable(
    script=script,
    base=base,
    targetName=target_name,
    icon=icon,
    initScript=None,
    compress=False,
    copyDependentFiles=True,
    appendScriptToExe=True,
    appendScriptToLibrary=True,
)

setup(
    version=__version__,
    name=__title__,
    description=__description__,
    author=__author__,
    options={
        'build_exe': {
            'includes': includes,
            'excludes': excludes,
            'packages': packages,
            'include_files': include_files,
        },
    },
    executables=[target]
)
