import os


def initialize():
    if os.name == 'nt':
        from clipmanager.paste.win32 import send_event
        return send_event
    elif os.name == 'posix':
        from clipmanager.paste.x11 import send_event
        return send_event
