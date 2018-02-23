import os
import re
import sys

from cx_Freeze import Executable, setup

ROOT = os.path.abspath(os.path.dirname(__file__))
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


def get_version():
    init = open(os.path.join(ROOT, 'clipmanager', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


python_install_dir, __ = os.path.split(sys.executable)
site_packages_path = os.path.join(python_install_dir, 'Lib', 'site-packages')

buildOptions = dict(
    optimize=2,
    include_msvcr=False,
    include_files=[
        (
            os.path.join(
                site_packages_path,
                'PySide',
                'plugins',
                'sqldrivers', 'qsqlite4.dll'
            ),
            os.path.join('sqldrivers', 'qsqlite4.dll')
        ),
    ],
    packages=[
        'pkg_resources',  # package dependencies are missed by cxfreeze
    ],
    excludes=[
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
