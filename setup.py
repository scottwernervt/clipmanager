#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import Command
    from setuptools import find_packages
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    from distutils.command.install_data import install_data
    from distutils.command.install import INSTALL_SCHEMES
    from distutils.sysconfig import get_python_lib


# Application specific data from package
version = __import__('clipmanager').__version__

from clipmanager.defs import APP_ORG as organization
from clipmanager.defs import APP_NAME as name
from clipmanager.defs import APP_DOMAIN as domain
from clipmanager.defs import APP_DESCRIPTION as description
from clipmanager.defs import APP_AUTHOR as author
from clipmanager.defs import APP_EMAIL as email


# Requires
required_packages = ['PySide (>=1.1.2)', 'keybinder (>=0.3.0)']

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
                  ('clipmanager/', ['clipmanager/license.txt']),
                  ('share/pixmaps', ['clipmanager/icons/clipamanger.ico'])]
)