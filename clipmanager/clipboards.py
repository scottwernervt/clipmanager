#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import subprocess
import sys

from PySide import QtCore
from PySide import QtGui

from settings import settings

# Windows API to get clipboard owner process name
if sys.platform.startswith('win32'):
    from ctypes import c_char
    from ctypes import windll
    from win32process import GetWindowThreadProcessId

logging.getLogger(__name__)

# Win32 only
MAX_PATH = 260
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400


class ClipBoards(QtCore.QObject):
    """Handles communication between all clipboards and main window.

    Source:
        http://bazaar.launchpad.net/~glipper-drivers/glipper/trunk/view/head:/glipper/Clipboards.py
    """

    def __init__(self, parent=None):
        super(ClipBoards, self).__init__(parent)
        self.parent = None
        logging.debug('test')

        # QApplication = QtCore.QCoreApplication.instance() # Access QApplication

        # TODO: Add Selection and Find Buffer clipboards
        # for Linux and OSX
        # http://lists.trolltech.com/qt-interest/2005-02/thread00940-0.html
        # if QApplication.clipbioard().supportsSelection():
        #   logging.debug('OS Supports Selection')
        #   # QClipboard.Mode = QClipboard.Selection
        #   self.clipboard_selection = Clipboard(QApplication.clipboard(QClipboard.Selection)
        #       , self.emit_new_item)

        # Primary clip board
        self.clip_board_global = ClipBoard(QtGui.QApplication.clipboard(),
                                           self.emit_new_item,
                                           QtGui.QClipboard.Clipboard, self)

    def clear(self):
        self.clip_board_global.clear()

    def get_global_clipboard_data(self):
        return self.clip_board_global.get_data()

    def set_data(self, mime_data):
        """Sets user select contents to all clipboards.

        Args:
            mime_data: QtCore.QMimeData
        """
        self.clip_board_global.set_data(mime_data)

    def emit_new_item(self, mime_data):
        """Emits new lipboard contents to main window.

        Args:
           mime_data: QtCore.QMimeData
        """
        self.emit(QtCore.SIGNAL('new-item(QMimeData)'), mime_data)


class ClipBoard(QtCore.QObject):
    """Handles monitoring each clipboard and perfoming actions on it.
    
    Todo:
        X11 selection
        OSX find buffer
    """

    def __init__(self, clip_board, new_item_callback, mode, parent=None):
        super(ClipBoard, self).__init__(parent)
        self.parent = parent

        self.clip_board = clip_board
        self.new_item_callback = new_item_callback
        self.mode = mode

        self.clipboard_contents = None

        self.connect(self.clip_board, QtCore.SIGNAL('dataChanged()'),
                     self.on_data_changed)

        self.connect(self.clip_board, QtCore.SIGNAL('ownerDestroyed()'),
                     self.on_owner_destroyed)

    def clear(self):
        if not settings.get_disconnect():
            self.clip_board.clear(mode=self.mode)

    def get_data(self):
        return self.clip_board.mimeData(self.mode)

    def set_data(self, mime_data):
        """Set mime_data to clipboard.
        
        Args:
            mime_data: QtCore.QMimeData 
        """
        if not settings.get_disconnect():
            logging.debug(str(self.mode))
            self.clip_board.setMimeData(mime_data, self.mode)

    def on_owner_destroyed(self):
        """X11 also has the concept of ownership.

        If you change the selection within a window, X11 will only notify the 
        owner and the previous owner of the change, i.e. it will not notify all 
        applications that the selection or clipboard data changed.
        """
        logging.debug('Owner destroyed!')
        if not settings.get_disconnect():
            self.new_item_callback(self.clipboard_contents)

    def on_data_changed(self):
        """Send clipboard mime data back to master clipboard class.
        """
        if not settings.get_disconnect():
            self.clipboard_contents = self.clip_board.mimeData(self.mode)
            self.new_item_callback(self.clipboard_contents)


def get_x11_owner():
    """Returns the active window as the best guess of clipboard owner.

    Assumes that the clipboard contents were changed by the user's active 
    window. Not sure if this is full proof as user might quickly switch
    windows.

    Returns:
        name (str): process name, i.e. KeyPass.exe
        name (None): no process owner found

    Source:
        http://stackoverflow.com/questions/3983946/get-active-window-title-in-x
        https://bbs.archlinux.org/viewtopic.php?id=113346
        http://stackoverflow.com/questions/2041532/getting-pid-and-details-for-topmost-window
    """
    name = None
    pid = None

    # Get active window PID
    # Method 1: xdotool
    cmd = 'xdotool getactivewindow getwindowpid'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    pid, err = process.communicate()
    errcode = process.returncode

    if errcode != 0:
        logging.debug('cmd: %s' % cmd)
        logging.warn('std.out: %s' % pid)
        logging.warn('std.err: %s' % err)
        logging.warn('exit: %s' % errcode)
        pid = None

    # Method 2: xprop
    if not pid:
        cmd = ("xprop -id $(xprop -root | awk '/_NET_ACTIVE_WINDOW\(WINDOW\)"
               "/{print $NF}') | awk '/_NET_WM_PID\(CARDINAL\)/{print $NF}'")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        pid, err = process.communicate()
        errcode = process.returncode

        # Return if failed to PID
        if errcode != 0:
            logging.debug('cmd: %s' % cmd)
            logging.warn('std.out: %s' % pid)
            logging.warn('std.err: %s' % err)
            logging.warn('exit: %s' % errcode)
            return None

    # Get path to binary from PID #
    cmd = 'readlink -f /proc/%s/exe' % pid.strip()
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    binary_path, err = process.communicate()
    errcode = process.returncode

    if errcode != 0:
        logging.debug('cmd: %s' % cmd)
        logging.warn('std.out: %s' % binary_path)
        logging.warn('std.err: %s' % err)
        logging.warn('exit: %s' % errcode)
        return name

    name = os.path.basename(binary_path).strip()
    logging.info(name)

    return name


def get_win32_owner():
    """Return the clipboard owner process name.

    Determines the process exe by determing the PID of the Window's ClipBoard
    owner.

    Returns:
        name (str): process name, i.e. KeyPass.exe
        name (None): no process owner found

    Source:
        http://nullege.com/codes/show/src%40w%40i%40winappdbg-1.4%40winappdbg%40system.py/5058/win32.GetProcessImageFileName/python
        http://stackoverflow.com/questions/6980246/how-can-i-find-a-process-by-name-and-kill-using-ctypes
        http://msdn.microsoft.com/en-us/library/windows/desktop/ms648709(v=vs.85).aspx
    """
    # HWND WINAPI GetClipboardOwner(void);
    owner_handle = windll.user32.GetClipboardOwner()
    logging.debug('owner_handle: %s' % owner_handle)

    # DWORD WINAPI GetWindowThreadProcessId(
    #   _In_       HWND hWnd,
    #   _Out_opt_  LPDWORD lpdwProcessId
    # );
    _, owner_pid = GetWindowThreadProcessId(owner_handle)
    logging.debug('owner_pid: %s' % owner_pid)

    # HANDLE WINAPI OpenProcess(
    #   _In_  DWORD dwDesiredAccess,
    #   _In_  BOOL bInheritHandle,
    #   _In_  DWORD dwProcessId
    # );
    pid_handle = windll.kernel32.OpenProcess(PROCESS_TERMINATE |
                                             PROCESS_QUERY_INFORMATION, False,
                                             owner_pid)
    logging.debug('pid_handle: %s' % pid_handle)

    ImageFileName = (c_char * MAX_PATH)()
    try:
        # DWORD WINAPI GetProcessImageFileName(
        #   _In_   HANDLE hProcess,
        #   _Out_  LPTSTR lpImageFileName,
        #   _In_   DWORD nSize
        # );
        if windll.psapi.GetProcessImageFileNameA(pid_handle, ImageFileName,
                                                 MAX_PATH) > 0:
            name = os.path.basename(ImageFileName.value)
        else:
            name = None
    except (AttributeError, WindowsError) as err:
        logging.exception(err)
        name = None

    # BOOL WINAPI CloseHandle(
    #   _In_  HANDLE hObject
    # );
    windll.kernel32.CloseHandle(pid_handle)

    logging.info('name: %s' % name)
    return name
