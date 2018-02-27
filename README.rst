ClipManager
===========

.. image:: https://travis-ci.org/scottwernervt/clipmanager.svg?branch=master
   :target: https://travis-ci.org/scottwernervt/clipmanager

.. image:: https://img.shields.io/badge/license-BSD-blue.svg
   :target: /LICENSE

.. image:: https://api.codeclimate.com/v1/badges/80e08076df90e2c5e23a/maintainability
    :target: https://codeclimate.com/github/scottwernervt/clipmanager/maintainability

Cross-platform (Windows and Linux) GUI application to manage the system's
clipboard history.

.. image:: https://i.imgur.com/NSVFd3b.png
   :alt: Main application screenshot
   :target: https://i.imgur.com/NSVFd3b.png

Requirements
------------

* Python 2.7
* PySide
* python-xlib (linux) or pywin32 (windows)
* PyInstaller (optional: win32 executable)
* Inno Setup (optional: win32 installer package)

Installation
------------

**Arch Linux**

`clipmanager <https://aur.archlinux.org/packages/clipmanager>`_

**Windows**

`clipmanager-setup-v0.4.0.exe <https://github.com/scottwernervt/clipmanager/releases/download/v0.4.0/clipmanager-setup-v0.4.0.exe>`_


Development
-----------

**Application Icon**

#. Navigate to `fa2png.io <http://fa2png.io/>`_
#. Icon = ``feather-clipboard``
#. Color = ``#ececec``
#. Background = ``transparent``
#. Size = ``256px``
#. Padding = ``24px``

**Build Resources**

``pyside-rcc -o data/resource_rc.py clipmanager/resource.qrc``

**Package Arch AUR**

.. code:: bash

    $ makepkg -g >> PKGBUILD
    $ namcap PKGBUILD
    $ makepkg -f
    $ namcap clipmanager-<version>-1-any.pkg.tar.xz
    $ makepkg -si
    $ makepkg --printsrcinfo > .SRCINFO

    $ git add PKGBUILD .SRCINFO
    $ git commit -m "useful commit message"
    $ git push

**Package Win32 Executable**

.. code:: bash

    > pyinstaller --noconfirm --clean clipmanager.spec
    > "C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin\signtool.exe" sign -f clipmanager.pfx -t http://timestamp.comodoca.com -p <PASSWORD> dist\clipmanager\clipmanager.exe
    > "C:\Program Files\Inno Setup 5\iscc.exe" "clipmanager.iss"
    > "C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin\signtool.exe" sign -f clipmanager.pfx -t http://timestamp.comodoca.com -p <PASSWORD> dist\clipmanager-setup-<VERSION>.exe

Help
----

**PyWin32: DLL load failed on Python 3.4b1**

`#661 DLL load failed on Python 3.4b1 <https://sourceforge.net/p/pywin32/bugs/661/>`_

.. code:: bash

    > copy C:\Python27\lib\site-packages\pywin32_system32\py*.dll C:\Python27\lib\site-packages\win32

**ClipManager is not using my GTK theme**

.. code:: bash

    $ ln -s icon/theme/directory $HOME/.icons/hicolor

Icons
-----

* `ClipManager application icon <https://github.com/feathericons/feather>`_
* `Menu icons <https://github.com/horst3180/arc-icon-theme>`_

Inspiration
-----------

* `Ditto Clipboard Manager <http://ditto-cp.sourceforge.net/>`_
* `Glipper <https://launchpad.net/glipper>`_
* `Clipit <http://clipit.rspwn.com/>`_
