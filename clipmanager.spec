# -*- mode: python -*-

import os
import sys

block_cipher = None

python_install_dir, _ = os.path.split(sys.executable)
site_packages_path = os.path.join(python_install_dir, 'Lib', 'site-packages')

a = Analysis(['bin\\clipmanager'],
             pathex=[],
             binaries=[
                 (
                     os.path.join(site_packages_path, 'PySide', 'plugins',
                                  'sqldrivers', 'qsqlite4.dll'),
                     os.path.join('qt4_plugins', 'sqldrivers'),
                 ),
             ],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='clipmanager',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='data\\clipmanager.ico',
          version='clipmanager.version')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='clipmanager')
