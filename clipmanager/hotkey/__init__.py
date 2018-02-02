import os


def initialize():
    if os.name == 'nt':
        pass
        # from gui.hotkeys.win32.global_hotkey_win import GlobalHotkeyManagerWin
        # return GlobalHotkeyManagerWin()
    elif os.name == 'posix':
        from clipmanager.hotkey.x11 import GlobalHotkeyManagerX11
        return GlobalHotkeyManagerX11()
