from ctypes import c_char
from ctypes import windll
from ctypes.wintypes import HWND
import os
from win32process import GetWindowThreadProcessId


MAX_PATH = 260
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400

GetClipboardOwner = windll.user32.GetClipboardOwner
GetClipboardOwner.restype = HWND
GetClipboardOwner.argtypes = []

def get_win32_process_name():
    clipboard_owner_handle = GetClipboardOwner()
    print 'owner_handle:',clipboard_owner_handle

    _, owner_pid = GetWindowThreadProcessId(clipboard_owner_handle)
    print 'pid:',owner_pid

    pid_handle = windll.kernel32.OpenProcess(PROCESS_TERMINATE | 
                                         PROCESS_QUERY_INFORMATION, False, 
                                        owner_pid)
    print 'pid_handle:',pid_handle

    ImageFileName = (c_char*MAX_PATH)()
    if windll.psapi.GetProcessImageFileNameA(pid_handle, ImageFileName, 
                                             MAX_PATH)>0:
        processname = os.path.basename(ImageFileName.value)
        print 'processname:',processname

    windll.kernel32.CloseHandle(pid_handle)


get_win32_process_name()