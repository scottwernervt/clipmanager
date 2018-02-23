#!/usr/bin/env python2

import os
import re
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

ROOT = os.path.abspath(os.path.dirname(__file__))
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


install_requires = ['pyside']
data_files = []

if os.name == 'nt':
    install_requires.append('pywin32')
elif os.name == 'posix':
    install_requires.append('python-xlib')
    data_files.extend([
        ('share/applications', ['clipmanager.desktop']),
        ('share/pixmaps', ['data/clipmanager.png']),
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
    long_description=open('README.rst').read(),
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
        'win32': [
            'PyInstaller',  # GPL
        ],
    },
    setup_requires=[
        'pytest-runner',  # MIT
    ],
    tests_require=[
        'pytest',  # MIT
        'pytest-qt',  # MIT
    ],
    test_suite='tests',
    packages=find_packages(exclude=['contrib', 'tests*']),
    include_package_data=True,
    data_files=data_files,
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Utilities',
    ]
)
