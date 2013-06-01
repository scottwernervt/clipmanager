#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import Command
from setuptools import find_packages
from setuptools import setup

# Application specific data from package
version = __import__('clipmanager').__version__

from clipmanager.defs import APP_ORG as organization
from clipmanager.defs import APP_NAME as name
from clipmanager.defs import APP_DOMAIN as domain
from clipmanager.defs import APP_DESCRIPTION as description
from clipmanager.defs import APP_AUTHOR as author
from clipmanager.defs import APP_EMAIL as email


# Requires
required_packages = ['PySide', 'keybinder',]

setup(
    scripts = ['bin/clipmanager'],
    name = name.lower(),
    version = version,
    description = description,
    license = 'BSD',

    author = author,
    author_email = email,
    maintainer = author,
    maintainer_email = author,
    url = domain,
    download_url = domain,

    platforms = ['unix', 'linux', 'win32'],
    requires = required_packages, 

    packages = ['clipmanager', 'clipmanager.paste', 'clipmanager.hotkey'],
    package_data = {
        'clipmanager': ['*.txt'],
        'clipmanager': ['icons/*.png', 'icons/*.ico'],
    },
    data_files = [('share/applications', ['clipmanager.desktop']),
                  ('clipmanager/', ['clipmanager/license.txt'])]
                  # ('share/clipmanager/pixmaps', ['clipmanager/icons/48x48/clipmanager.png']),
                  # ('share/icons/hicolor/16x16/apps', ['clipmanager/icons/16x16/clipmanager.png']),
                  # ('share/icons/hicolor/22x22/apps', ['clipmanager/icons/22x22/clipmanager.png']),
                  # ('share/icons/hicolor/48x48/apps', ['clipmanager/icons/48x48/clipmanager.png'])]
)