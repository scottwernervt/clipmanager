#!/usr/bin/env python2

import os
import re

from setuptools import find_packages, setup

ROOT = os.path.abspath(os.path.dirname(__file__))
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')

install_requires = ['PySide']
data_files = []

if os.name == 'nt':
    install_requires.append('pywin32')
elif os.name == 'posix':
    install_requires.append('python-xlib')
    data_files.extend([
        ('share/applications', ['clipmanager.desktop']),
        ('share/pixmaps', ['clipmanager/icons/clipmanager.png']),
        ('/etc/xdg/autostart', ['clipmanager-autostart.desktop'])
    ])


def get_version():
    init = open(os.path.join(ROOT, 'clipmanager', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


download_url = 'https://github.com/scottwernervt/clipmanager' \
               'archive/%s.tar.gz' % get_version()

setup(
    name='clipmanager',
    version=get_version(),
    author='Scott Werner',
    author_email='scott.werner.vt@gmail.com',
    description="Manage the system's clipboard history.",
    long_description=open('README.md').read(),
    license='BSD',
    platforms='Posix; Windows',
    keywords=' '.join([
        'clipboard',
        'manager',
        'history',
    ]),
    url='https://github.com/scottwernervt/clipmanager',
    download_url=download_url,
    scripts=['bin/clipmanager'],
    install_requires=install_requires,
    extras_require={
        'tests': [
            'pytest',  # MIT
        ],
        'windows': [
            'cx_Freeze',  # PSF
        ],
    },
    setup_requires=[
        'pytest-runner',  # MIT
    ],
    tests_require=[
        'pytest',  # MIT
    ],
    packages=find_packages(exclude=['contrib', 'tests*']),
    include_package_data=True,
    package_data={'clipmanager': ['icons/*.png', 'icons/*.ico']},
    data_files=data_files,
)
