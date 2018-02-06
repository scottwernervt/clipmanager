import logging
import os
import subprocess

from PySide.QtCore import QObject, SIGNAL, Slot
from PySide.QtGui import QApplication, QClipboard

from clipmanager.settings import settings

if os.name == 'nt':
    from ctypes import c_char
    from ctypes import windll
    from win32process import GetWindowThreadProcessId

logger = logging.getLogger(__name__)

# Win32 only
MAX_PATH = 260
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400


def x11_owner():
    """Returns the active window as the best guess of clipboard owner.

    Assumes that the clipboard contents were emit_new_item by the user's active
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
        logger.warn('std.out: %s' % pid)
        logger.warn('std.err: %s' % err)
        logger.warn('exit: %s' % errcode)
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
            logger.warn('std.out: %s' % pid)
            logger.warn('std.err: %s' % err)
            logger.warn('exit: %s' % errcode)
            return None

    # Get path to binary from PID #
    cmd = 'readlink -f /proc/%s/exe' % pid.strip()
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    binary_path, err = process.communicate()
    errcode = process.returncode

    if errcode != 0:
        logger.warn('std.out: %s' % binary_path)
        logger.warn('std.err: %s' % err)
        logger.warn('exit: %s' % errcode)
        return name

    name = os.path.basename(binary_path).strip()

    logger.info(name)
    return name


def win32_owner():
    """Return the clipboard owner process name.

    Determines the process exe by determing the PID of the Window's Clipboard
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

    # DWORD WINAPI GetWindowThreadProcessId(
    #   _In_       HWND hWnd,
    #   _Out_opt_  LPDWORD lpdwProcessId
    # );
    _, owner_pid = GetWindowThreadProcessId(owner_handle)

    # HANDLE WINAPI OpenProcess(
    #   _In_  DWORD dwDesiredAccess,
    #   _In_  BOOL bInheritHandle,
    #   _In_  DWORD dwProcessId
    # );
    pid_handle = windll.kernel32.OpenProcess(PROCESS_TERMINATE |
                                             PROCESS_QUERY_INFORMATION, False,
                                             owner_pid)

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
        logger.exception(err)
        name = None

    # BOOL WINAPI CloseHandle(
    #   _In_  HANDLE hObject
    # );
    windll.kernel32.CloseHandle(pid_handle)

    logger.debug(name)
    return name


class ClipboardManager(QObject):
    """Handles communication between all clipboards and main window.

    Source: http://bazaar.launchpad.net/~glipper-drivers/glipper/trunk/view/head:/glipper/Clipboards.py
    """

    def __init__(self, parent=None):
        super(ClipboardManager, self).__init__(parent)

        self.primary_clipboard = Clipboard(QApplication.clipboard(),
                                           self.emit_new_item,
                                           QClipboard.Clipboard)

    def get_primary_clipboard_text(self):
        """Get primary clipboard contents.

        :return: Current clipboard contents.
        :rtype: QMimeData
        """
        return self.primary_clipboard.get_text()

    def set_text(self, mime_data):
        """Set clipboard contents.

        :param mime_data: Data to set to global clipboard.
        :type mime_data: QMimeData

        :return: None
        :rtype: None
        """
        self.primary_clipboard.set_text(mime_data)
        self.emit_new_item(mime_data)

    def clear_text(self):
        self.primary_clipboard.clear_text()

    def emit_new_item(self, mime_data):
        """Emits new clipboard contents to main window.

        Args:
           mime_data: QMimeData
        """
        self.emit(SIGNAL('newItem(QMimeData)'), mime_data)


class Clipboard(QObject):
    """Monitor's clipboard for changes.

    :param clipboard: Clipboard reference.
    :type clipboard: QClipboard

    :param new_item_callback: Function to call on content change.
    :type new_item_callback: pyfunc

    :param mode:
    :type mode: QClipboard.Mode.Clipboard

    :param parent: Clipboard manager.
    :type parent: ClipboardManager
    """

    def __init__(self, clipboard, new_item_callback, mode):
        super(Clipboard, self).__init__()

        self.clipboard = clipboard
        self.new_item_callback = new_item_callback
        self.mode = mode

        self.connect(self.clipboard, SIGNAL('dataChanged()'),
                     self.on_data_changed)

        self.connect(self.clipboard, SIGNAL('ownerDestroyed()'),
                     self.on_owner_change)

    def get_text(self):
        """Get clipboard contents.

        :return: Current clipboard contents.
        :rtype: QMimeData
        """
        return self.clipboard.mimeData(self.mode)

    def set_text(self, mime_data):
        """Set clipboard contents.

        :param mime_data: Data to set to global clipboard.
        :type mime_data: QMimeData

        :return: None
        :rtype: None
        """
        if not settings.get_disconnect():
            self.clipboard.setMimeData(mime_data, self.mode)

    def clear_text(self):
        """Clear clipboard contents.

        :return: None
        :rtype: None
        """
        if not settings.get_disconnect():
            self.clipboard.clear(mode=self.mode)

    @Slot()
    def on_owner_change(self):
        """Handle X11 ownership destruction.

        If you change the selection within a window, X11 will only notify the
        owner and the previous owner of the change, i.e. it will not notify all
        applications that the selection or clipboard data emit_new_item.

        :return: None
        :rtype: None
        """
        if not settings.get_disconnect():
            self.new_item_callback(self.contents)

    @Slot()
    def on_data_changed(self):
        """Add new clipboard item using callback.

        :return: None
        :rtype: None
        """
        if not settings.get_disconnect():
            self.new_item_callback(self.get_text())
