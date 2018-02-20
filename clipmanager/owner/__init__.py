import os


def initialize():
    if os.name == 'nt':
        from clipmanager.owner.win32 import get_win32_owner
        return get_win32_owner
    elif os.name == 'posix':
        from clipmanager.owner.x11 import get_x11_owner
        return get_x11_owner
