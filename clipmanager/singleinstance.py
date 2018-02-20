import logging
import os
import tempfile

from clipmanager import __name__, __org__

if os.name == 'nt':
    from win32event import CreateMutex
    from win32api import CloseHandle, GetLastError
    from winerror import ERROR_ALREADY_EXISTS
else:
    import commands
    import os

logger = logging.getLogger(__name__)


class SingleInstance:
    """Limits application to a single instance.

    References
    - https://github.com/josephturnerjr/boatshoes/blob/master/boatshoes/SingleInstance.py
    - https://github.com/csuarez/emesene-1.6.3-fixed/blob/master/SingleInstance.py
    """

    def __init__(self):
        self.last_error = False
        self.pid_path = os.path.normpath(
            os.path.join(
                tempfile.gettempdir(),
                '%s-%s.lock' % (__name__.lower(), self._get_username())
            )
        )

        if os.name == 'nt':
            # HANDLE WINAPI CreateMutex(
            #   _In_opt_  LPSECURITY_ATTRIBUTES lpMutexAttributes,
            #   _In_      BOOL bInitialOwner,
            #   _In_opt_  LPCTSTR lpName
            # );
            #
            # DWORD WINAPI GetLastError(void);
            self.mutex_name = '%s.%s' % (__org__, __name__)
            self.mutex = CreateMutex(None, False, self.mutex_name)
            self.last_error = GetLastError()
        else:
            if os.path.exists(self.pid_path):
                pid = open(self.pid_path, 'r').read().strip()
                pid_running = commands.getoutput('ls /proc | grep %s' % pid)

                if pid_running:
                    self.last_error = True

            if not self.last_error:
                f = open(self.pid_path, 'w')
                f.write(str(os.getpid()))
                f.close()

    def __del__(self):
        self.destroy()

    @staticmethod
    def _get_username():
        return os.getenv('USERNAME') or os.getenv('USER')

    def is_running(self):
        """Check if application is running.

        :return: True if instance is running.
        :rtype: bool
        """
        if os.name == 'nt':
            # ERROR_ALREADY_EXISTS
            # 183 (0xB7)
            # Cannot create a file when that file already exists.
            return self.last_error == ERROR_ALREADY_EXISTS
        else:
            return self.last_error

    def destroy(self):
        """Close mutex handle or delete pid file.

        :return: None
        :rtype: None
        """
        if os.name == 'nt' and self.mutex:
            # BOOL WINAPI CloseHandle(
            #   _In_  HANDLE hObject
            # );
            CloseHandle(self.mutex)
        else:
            try:
                os.unlink(self.pid_path)
            except OSError as err:
                logger.error(err)
