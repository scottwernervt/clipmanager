import logging
import os
from ctypes import c_char, windll

from win32gui import EnumWindows, GetWindowText
from win32process import GetWindowThreadProcessId

logger = logging.getLogger(__name__)

MAX_PATH = 260
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400


def get_hwnds_for_pid(pid):
    """Get HWND's for particular PID.

    Source:
    http://timgolden.me.uk/python/win32_how_do_i/find-the-window-for-my-subprocess.html

    :param pid: Process identifier to look up.
    :type pid: int

    :return: List of window handles
    :rtype: list
    """

    def callback(hwnd, hwnds):
        _, found_pid = GetWindowThreadProcessId(hwnd)
        if found_pid == pid:
            hwnds.append(hwnd)
        return True

    hwnds = []
    EnumWindows(callback, hwnds)
    return hwnds


def get_win32_owner():
    """Get clipboard owner window details.

    Sources:
    https://sjohannes.wordpress.com/2012/03/23/win32-python-getting-all-window-titles/
    http://nullege.com/codes/show/src%40w%40i%40winappdbg-1.4%40winappdbg%40system.py/5058/win32.GetProcessImageFileName/python
    http://stackoverflow.com/questions/6980246/how-can-i-find-a-process-by-name-and-kill-using-ctypes
    http://msdn.microsoft.com/en-us/library/windows/desktop/ms648709(v=vs.85).aspx

    :return: List of clipboard owner's binary name and window titles/classes.
    :rtype: list[str]
    """
    owner_names = []

    # HWND WINAPI GetClipboardOwner(void);
    owner_hwnd = windll.user32.GetClipboardOwner()

    # DWORD WINAPI GetWindowThreadProcessId(
    #   _In_       HWND hWnd,
    #   _Out_opt_  LPDWORD lpdwProcessId
    # );
    _, owner_process_id = GetWindowThreadProcessId(owner_hwnd)

    for hwnd in get_hwnds_for_pid(owner_process_id):
        window_text = GetWindowText(hwnd)
        if window_text:
            window_title = window_text.split('-')[-1].strip()
            owner_names.extend([window_text, window_title])

    # HANDLE WINAPI OpenProcess(
    #   _In_  DWORD dwDesiredAccess,
    #   _In_  BOOL bInheritHandle,
    #   _In_  DWORD dwProcessId
    # );
    h_process = windll.kernel32.OpenProcess(PROCESS_TERMINATE |
                                            PROCESS_QUERY_INFORMATION, False,
                                            owner_process_id)

    ImageFileName = (c_char * MAX_PATH)()

    try:
        # DWORD WINAPI GetProcessImageFileName(
        #   _In_   HANDLE hProcess,
        #   _Out_  LPTSTR lpImageFileName,
        #   _In_   DWORD nSize
        # );
        if windll.psapi.GetProcessImageFileNameA(h_process, ImageFileName,
                                                 MAX_PATH) > 0:
            binary_name = os.path.basename(ImageFileName.value)
            if binary_name:
                owner_names.append(binary_name)
    except (AttributeError, WindowsError) as err:
        logger.exception(err)

    # BOOL WINAPI CloseHandle(
    #   _In_  HANDLE hObject
    # );
    windll.kernel32.CloseHandle(h_process)

    logger.debug('%s', owner_names)
    return owner_names
