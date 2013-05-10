#!/usr/bin/python
# -*- coding: utf-8 -*-
# http://www.siafoo.net/article/77

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
from distutils.sysconfig import get_python_lib
import os
import sys

version = __import__('clipmanager').__version__
# print version

setup(
	name='ClipManager',
	version=version,
	description='Manage clipboard history',
	author='Scott Werner',
	author_email='scott.werner.vt@gmail.com',
	maintainer='Scott Werner',
	maintainer_email='scott.werner.vt@gmail.com',
	url='http://mercnet.github.com/clipman/',
	license='GNU GPL v2',
    packages = ['clipmanager'],
    cmdclass = {'install_data': install_data},
    data_files = [['clipmanager/icons', 
                    ['clipmanager/icons/exit.png'
                    ,'clipmanager/icons/add.png'
                    , 'clipmanager/icons/search.png'
                    , 'clipmanager/icons/app.ico'
                    , 'clipmanager/icons/remove.png'
                    , 'clipmanager/icons/settings.png'
                    , 'clipmanager/icons/disconnect.png'
                    , 'clipmanager/icons/about.png']
                    ],
                   ['clipmanager', ['clipmanager/license.txt']],
                   ['/usr/share/applications', ['clipmanager.desktop']],
                ],
    scripts = ['bin/clipmanager'],
    requires=['PySide (>=1.1.2)'], # Add gtk and keybinder
  )
