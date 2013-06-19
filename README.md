# ClipManager
Cross-platform (Windows and Linux) GUI application to manage the history of the system's clipboard. 

![ClipManager main screenshot](http://i.imgur.com/myDxq5r.png "ClipManager main screenshot")

[Application settings](http://i.imgur.com/3VVXFI4.png) and [history preview](http://i.imgur.com/DeaeSqp.png) screenshots.

## Installation
**Windows**

Download the latest installer at [clipmanager-setup-0.3.exe](https://bitbucket.org/mercnet/clipmanager/downloads/clipmanager-setup-0.3.exe).

**Ubuntu**

[launchpad.net](https://launchpad.net/~mercnet/+archive/clipmanager)

    sudo add-apt-repository ppa:mercnet/clipmanager
    sudo apt-get install clipmanager

**Arch**

[aur.archlinux.org](https://aur.archlinux.org/packages/clipmanager) | [Install Yaourt](https://wiki.archlinux.org/index.php/Yaourt#Installation)

    yaourt -S clipmanager


## Build Requirements
**All Platforms**

* Python 2.7
* PySide 1.1.2
* [setuptools](https://pypi.python.org/pypi/setuptools)
* _Optional_
	* [cx_Freeze](http://cx-freeze.sourceforge.net/) to create an executable or binary.
	* [py.test](http://pytest.org/latest/) to run unit tests.

**Windows**

* [pywin32](http://sourceforge.net/projects/pywin32/files/)
* _Optional_
	* [Inno Setup](http://www.jrsoftware.org/isinfo.php) to create a Windows installer package.

**Linux**

* [python-keybinder](https://github.com/engla/keybinder)

## Todo
1. Support X11 selection clipboard.
1. Support OSX. 
1. Capture images and display them in history.


## Contributors
* [Scott Werner](http://www.linkedin.com/in/scottwernervt) <<scott.werner.vt@gmail.com>>, alias [mercnet](https://bitbucket.org/mercnet)
* I am looking for code mentoring/tips as this is my first public application.

## Inspiration
* [Ditto Clipboard Manager](http://ditto-cp.sourceforge.net/)
* [Glipper](https://launchpad.net/glipper)
* [Clipit](http://clipit.rspwn.com/)