#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import Command
from setuptools import find_packages
from setuptools import setup

# Application specific data from package
version = __import__('clipmanager').__version__


# Requires
required_packages = ['PySide', 'keybinder',]

setup(
    scripts = ['bin/clipmanager'],
    name = 'clipmanager',
    version = version,
    description = "Manage the system's clipboard history.",
    license = 'BSD',
    author = 'Scott Werner',
    author_email = 'scott.werner.vt@gmail.com',
    maintainer = 'Scott Werner',
    maintainer_email = 'scott.werner.vt@gmail.com',
    url = 'https://bitbucket.org/mercnet/clipmanager',
    download_url = 'https://bitbucket.org/mercnet/clipmanager',
    include_package_data = True,
    platforms = ['unix', 'linux', 'win32'],
    requires = required_packages, 
    packages = ['clipmanager', 'clipmanager.paste', 'clipmanager.hotkey'],
    package_data = {
        'clipmanager': ['*.txt'],
        'clipmanager': ['icons/*.png', 'icons/*.ico'],
    },
    data_files = [('share/applications', ['clipmanager.desktop']),
                  ('/etc/xdg/autostart', ['clipmanager-autostart.desktop']),
                  ('share/pixmaps', ['clipmanager/icons/clipmanager.png'])]
)