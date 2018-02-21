ClipManager
===========

.. image:: https://travis-ci.org/scottwernervt/clipmanager.svg?branch=master
    :target: https://travis-ci.org/scottwernervt/clipmanager

.. image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: /LICENSE

Cross-platform (Windows and Linux) GUI application to manage the system's
clipboard history.

.. image:: http://i.imgur.com/myDxq5r.png
    :alt: Main screenshot
   :target: http://i.imgur.com/myDxq5r.png

Requirements
------------
* Python 2.7
* PySide
* python-xlib (optional: for linux)
* pywin32 (optional: for windows)
* cx_Freeze (optional: build executable)
* Inno Setup (optional: windows installer package)

Installation
------------


Development
-----------

^^^^^
Linux
^^^^^
* [qt4](https://www.archlinux.org/packages/extra/x86_64/qt4/)
* [qtwebkit](https://aur.archlinux.org/packages/qtwebkit/)

Help
----

========================================
PyWin32: DLL load failed on Python 3.4b1
========================================

`#661 DLL load failed on Python 3.4b1 <https://sourceforge.net/p/pywin32/bugs/661/)>`_

.. code:: bash

    copy C:\Python27\lib\site-packages\pywin32_system32\py*.dll C:\Python27\lib\site-packages\win32

=====================================
ClipManager is not using my GTK theme
=====================================

.. code:: bash

    $ ln -s icon/theme/directory $HOME/.icons/hicolor

Inspiration
-----------
* `Ditto Clipboard Manager <http://ditto-cp.sourceforge.net/>`_
* `Glipper <https://launchpad.net/glipper>`_
* `Clipit <http://clipit.rspwn.com/>`_
