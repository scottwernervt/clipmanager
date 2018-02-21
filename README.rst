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
- Python 2.7
- PySide
- python-xlib (optional: for linux)
- pywin32 (optional: for windows)

Installation
------------


Development
-----------

#### Arch
* [qt4](https://www.archlinux.org/packages/extra/x86_64/qt4/)
* [qtwebkit](https://aur.archlinux.org/packages/qtwebkit/)

### Windows
* [pywin32](http://sourceforge.net/projects/pywin32/files/) - [#661 DLL load failed on Python 3.4b1](https://sourceforge.net/p/pywin32/bugs/661/)
 
    `copy C:\Python27\lib\site-packages\pywin32_system32\py*.dll C:\Python27\lib\site-packages\win32`

* [cx_Freeze](http://cx-freeze.sourceforge.net/) to create an executable or binary.
* [Inno Setup](http://www.jrsoftware.org/isinfo.php) to create a Windows installer package.


Help
----

========================================
PyWin32: DLL load failed on Python 3.4b1
========================================

`#661 DLL load failed on Python 3.4b1 <https://sourceforge.net/p/pywin32/bugs/661/)>`_

::

    copy C:\Python27\lib\site-packages\pywin32_system32\py*.dll C:\Python27\lib\site-packages\win32`

=====================================
ClipManager is not using my GTK theme
=====================================

::

    $ ln -s icon/theme/directory $HOME/.icons/hicolor

Inspiration
-----------
- [Ditto Clipboard Manager](http://ditto-cp.sourceforge.net/)
- [Glipper](https://launchpad.net/glipper)
- [Clipit](http://clipit.rspwn.com/)
