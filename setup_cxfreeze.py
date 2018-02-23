import os
import re

from cx_Freeze import Executable, setup

ROOT = os.path.abspath(os.path.dirname(__file__))
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


def get_version():
    init = open(os.path.join(ROOT, 'clipmanager', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=[
    'ctypes',
    'datetime',
    'itertools',
    'logging',
    'operator',
    'optparse',
    'os',
    'pkg_resources',
    'PySide.QtCore',
    'PySide.QtGui',
    'PySide.QtNetwork',
    'PySide.QtSql',
    'PySide.QtWebKit',
    're',
    'struct',
    'subprocess',
    'sys',
    'tempfile',
    'textwrap',
    'win32gui',
    'win32process',
    'zlib',
], excludes=[
    'json',
    'Tkinter',
    'unittest',
    'Xlib',
    'xml',
])

executables = [
    Executable(
        'clipmanager/app.py',
        base='Win32GUI',
        targetName='clipmanager.exe',
        icon='clipmanager/icons/clipmanager.ico'
    )
]

setup(name='clipmanager',
      version=get_version(),
      description="Manage the system's clipboard history.",
      options=dict(build_exe=buildOptions),
      executables=executables)
