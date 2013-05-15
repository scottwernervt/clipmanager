#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TEST LINUX:
# https://github.com/josephturnerjr/boatshoes/blob/master/boatshoes/SingleInstance.py
# https://github.com/csuarez/emesene-1.6.3-fixed/blob/master/SingleInstance.py

import logging
import sys

if sys.platform.startswith('win32'):
    from win32event import CreateMutex
    from win32api import CloseHandle, GetLastError
    from winerror import ERROR_ALREADY_EXISTS
else:
    import commands
    import os

from defs import APP_DOMAIN
from defs import APP_ORG
from defs import APP_NAME
from defs import APP_VERSION

logging.getLogger(__name__)


class SingleInstance(object):
    """Limits application to single instance on Windows and Linux.
    """
    def __init__(self):
        self.last_error = False

        if sys.platform.startswith('win32'):
            # HANDLE WINAPI CreateMutex(
            #   _In_opt_  LPSECURITY_ATTRIBUTES lpMutexAttributes,
            #   _In_      BOOL bInitialOwner,
            #   _In_opt_  LPCTSTR lpName
            # );
            # 
            # DWORD WINAPI GetLastError(void);
            self.mutex_name = '%s.%s' % (APP_ORG, APP_NAME)
            self.mutex = CreateMutex(None, False, self.mutex_name)
            self.last_error = GetLastError()
        else:
            self.pid_path = '/tmp/clipmanager.pid'
            if os.path.exists(self.pid_path):
                pid = open(self.pid_path, 'r').read().strip()
                pid_running = commands.getoutput('ls /proc | grep %s' % pid)

                if pid_running:
                    self.last_error = True

            if not self.last_error:
                f = open(self.pid_path, 'w')
                f.write(str(os.getpid()))
                f.close()

    def is_running(self):
        """Check if application is running.

        Returns:
            True/False
        """
        if sys.platform.startswith('win32'):
            # ERROR_ALREADY_EXISTS
            # 183 (0xB7)
            # Cannot create a file when that file already exists.
            return (self.last_error == ERROR_ALREADY_EXISTS)
        else:
            return self.last_error

    def __del__(self):
        """Close out mutex handle on exit. Note, handle automatically closed if
        process is terminated.
        """
        if sys.platform.startswith('win32'):
            if self.mutex:
                # BOOL WINAPI CloseHandle(
                #   _In_  HANDLE hObject
                # );
                CloseHandle(self.mutex)
        else:
            if not self.last_error:
                os.unlink(self.pid_path)

