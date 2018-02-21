# ClipManager

[![travis build status](https://travis-ci.org/scottwernervt/clipmanager.svg?branch=master)](https://travis-ci.org/scottwernervt/clipmanager)

Cross-platform (Windows and Linux) GUI application to manage the system's clipboard history.

![ClipManager main screenshot](http://i.imgur.com/myDxq5r.png "ClipManager main screenshot")

[Application settings](http://i.imgur.com/3VVXFI4.png) and [history preview](http://i.imgur.com/DeaeSqp.png) screenshots.

## Installation

### Windows

## Build Requirements

### Linux

#### Arch
* [qt4](https://www.archlinux.org/packages/extra/x86_64/qt4/)
* [qtwebkit](https://aur.archlinux.org/packages/qtwebkit/)

### Windows
* [pywin32](http://sourceforge.net/projects/pywin32/files/) - [#661 DLL load failed on Python 3.4b1](https://sourceforge.net/p/pywin32/bugs/661/)
 
    `copy C:\Python27\lib\site-packages\pywin32_system32\py*.dll C:\Python27\lib\site-packages\win32`

* [cx_Freeze](http://cx-freeze.sourceforge.net/) to create an executable or binary.
* [Inno Setup](http://www.jrsoftware.org/isinfo.php) to create a Windows installer package.


## Help

### ClipManager is not using my GTK theme

`$ ln -s icon/theme/directory $HOME/.icons/hicolor`

## Inspiration
* [Ditto Clipboard Manager](http://ditto-cp.sourceforge.net/)
* [Glipper](https://launchpad.net/glipper)
* [Clipit](http://clipit.rspwn.com/)
