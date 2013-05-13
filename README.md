# ClipManager
Cross-platform (Windows and Linux) GUI application to manage the history of the system's clipboard. 

![ClipManager main screenshot](http://i.imgur.com/myDxq5r.png "ClipManager main screenshot")

[Application settings](http://i.imgur.com/3VVXFI4.png) and [history preview](http://i.imgur.com/DeaeSqp.png) screenshots.

## Installation
**Windows**

Download installer at [link here]

**Linux**

    arch: yaourt -S {package-name}
    ubuntu: sudo apt-get install {package-name}
    redhat: sudo yum install {package-name}


## Build Requirements
**All Platforms**

* Python 2.7
* PySide 1.1.2
* _Optional_ [cx_Freeze](http://cx-freeze.sourceforge.net/) to create an executable or binary.

**Windows**

* [pywin32 218](http://sourceforge.net/projects/pywin32/files/)
* _Optional_ [Inno Setup](http://www.jrsoftware.org/isinfo.php) to create a Windows installer package.

**Linux**

* [python-keybinder 0.3.0](https://github.com/engla/keybinder)

## Todo
1. Support X11 selection clipboard.
1. Support OSX. 
1. Capture images and display them in history.


## Contributors
* [Scott Werner](http://www.linkedin.com/in/scottwernervt) <scott.werner.vt@gmail.com>, alias [mercnet](https://bitbucket.org/mercnet)


## Inspiration
* [Ditto Clipboard Manager](http://ditto-cp.sourceforge.net/)
* [Glipper](https://launchpad.net/glipper)
* [Clipit](http://clipit.rspwn.com/)