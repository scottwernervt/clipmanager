#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

from defs import APP_DOMAIN
from defs import APP_ORG
from defs import APP_NAME
from defs import APP_VERSION

logging.getLogger(__name__)


# Todo:
#       Write linux class to create a lock file on the PID. --> https://github.com/wiliamsouza/guanandy/blob/master/Guanandy/SingleInstance.py
#       Combine classes and use if sys.platform.startswith()

# Platform dependent modules
single_instance = None
if sys.platform.startswith('linux'):
    class LinuxSingleInstance(object):

        def __init__(self):
            pass

        def already_running(self):
            return False

    single_instance = LinuxSingleInstance()


elif sys.platform.startswith('win32'):
    from win32event import CreateMutex
    from win32api import CloseHandle, GetLastError
    from winerror import ERROR_ALREADY_EXISTS

    class WinSingleInstance(object):
        """Limits application to single instance on Windows.
        """
        def __init__(self):
            """Create mutex name based on application organization and name.

            HANDLE WINAPI CreateMutex(
              _In_opt_  LPSECURITY_ATTRIBUTES lpMutexAttributes,
              _In_      BOOL bInitialOwner,
              _In_opt_  LPCTSTR lpName
            );

            DWORD WINAPI GetLastError(void);
            """
            self.mutexname = '%s.%s' % (APP_ORG, APP_NAME)
            self.mutex = CreateMutex(None, False, self.mutexname)
            self.lasterror = GetLastError()
        
        def already_running(self):
            """Check if application is running.

            ERROR_ALREADY_EXISTS
                183 (0xB7)
                Cannot create a file when that file already exists.

            Returns:
                True/False
            """
            return (self.lasterror == ERROR_ALREADY_EXISTS)
            
        def __del__(self):
            """Close out mutex handle on exit. Note, handle automatically 
            closed if process is terminated.

            BOOL WINAPI CloseHandle(
              _In_  HANDLE hObject
            );
            """
            if self.mutex:
                CloseHandle(self.mutex)

    single_instance = WinSingleInstance()