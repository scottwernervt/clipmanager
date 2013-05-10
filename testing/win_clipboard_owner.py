#!/usr/bin/env python
# -*- coding: utf-8 -*-

# REFERNECE:


import logging
logging.getLogger(__name__)

from ctypes import c_char
from ctypes import create_unicode_buffer
from ctypes import windll
from ctypes.wintypes import HWND
from ctypes.wintypes import DWORD
import os
from win32process import GetWindowThreadProcessId

MAX_PATH = 260
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400

# GetClipboardOwner = windll.user32.GetClipboardOwner
# GetClipboardOwner.restype = HWND
# GetClipboardOwner.argtypes = []

def get_win32_process_name():
    """Return the clipboard owner process name.

    Returns:
        name (str): 
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

    ImageFileName = (c_char*MAX_PATH)()
    try:
        # DWORD WINAPI GetProcessImageFileName(
        #   _In_   HANDLE hProcess,
        #   _Out_  LPTSTR lpImageFileName,
        #   _In_   DWORD nSize
        # );
        if windll.psapi.GetProcessImageFileNameA(pid_handle, ImageFileName, 
                                                 MAX_PATH)>0:
            name = os.path.basename(ImageFileName.value)
        else:
            name = None
    except (AttributeError, WindowsError) as err:
        logging.exception(err)
        name = None

    windll.kernel32.CloseHandle(pid_handle)
    logging.debug('name: %s' % name)

    return name

get_win32_process_name()