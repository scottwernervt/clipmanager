import os


def initialize():
    if os.name == 'nt':
        from clipmanager.paste.win32 import paste_action
        return paste_action
    elif os.name == 'posix':
        from clipmanager.paste.x11 import paste_action
        return paste_action
