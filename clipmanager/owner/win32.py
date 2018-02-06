import logging
import os
from ctypes import c_char, windll

from win32process import GetWindowThreadProcessId

logger = logging.getLogger(__name__)

MAX_PATH = 260
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400


def get_win32_owner():
    """Return the clipboard owner process name.

    Determines the process exe by determining the PID of the Window's Clipboard
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
