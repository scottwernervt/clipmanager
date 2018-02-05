import os


def initialize():
    if os.name == 'nt':
        from clipmanager.hotkey.win32 import GlobalHotkeyManagerWin
        return GlobalHotkeyManagerWin()
    elif os.name == 'posix':
        from clipmanager.hotkey.x11 import GlobalHotkeyManagerX11
        return GlobalHotkeyManagerX11()
