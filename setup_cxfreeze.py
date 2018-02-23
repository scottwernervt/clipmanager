import os
import re
import sys

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
    'logging',
    'os',
    'pkg_resources',
    'textwrap',
    're',
    'subprocess',
    'sys',
    'zlib',
    'PySide.QtCore',
    'PySide.QtGui',
    'PySide.QtSql',
    'PySide.QtNetwork',
    'PySide.QtWebKit',
], excludes=[
    'email',
    'json',
    'unittest',
    'xml'
])

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('clipmanager/app.py', base=base, targetName='clipmanager.exe')
]

setup(name='clipmanager',
      version=get_version(),
      description="Manage the system's clipboard history.",
      options=dict(build_exe=buildOptions),
      executables=executables)
