"""
Source: https://github.com/rokups/paste2box
License: GNU General Public License v3.0
"""

import ctypes
import logging
from ctypes import POINTER
from ctypes.wintypes import BOOL, MSG

from PySide.QtCore import QTimer, Qt

from clipmanager.hotkey.base import GlobalHotkeyManagerBase
from clipmanager.hotkey.hook import hotpatch, unhotpatch

logging.getLogger(__name__)

VK_LBUTTON = 0x01  # Left mouse button
VK_RBUTTON = 0x02  # Right mouse button
VK_CANCEL = 0x03  # Control-break processing
VK_MBUTTON = 0x04  # Middle mouse button (three-button mouse)
VK_BACK = 0x08  # BACKSPACE key
VK_TAB = 0x09  # TAB key
VK_CLEAR = 0x0C  # CLEAR key
VK_RETURN = 0x0D  # ENTER key
VK_SHIFT = 0x10  # SHIFT key
VK_CONTROL = 0x11  # CTRL key
VK_MENU = 0x12  # ALT key
VK_PAUSE = 0x13  # PAUSE key
VK_CAPITAL = 0x14  # CAPS LOCK key
VK_ESCAPE = 0x1B  # ESC key
VK_SPACE = 0x20  # SPACEBAR
VK_PRIOR = 0x21  # PAGE UP key
VK_NEXT = 0x22  # PAGE DOWN key
VK_END = 0x23  # END key
VK_HOME = 0x24  # HOME key
VK_LEFT = 0x25  # LEFT ARROW key
VK_UP = 0x26  # UP ARROW key
VK_RIGHT = 0x27  # RIGHT ARROW key
VK_DOWN = 0x28  # DOWN ARROW key
VK_SELECT = 0x29  # SELECT key
VK_PRINT = 0x2A  # PRINT key
VK_EXECUTE = 0x2B  # EXECUTE key
VK_SNAPSHOT = 0x2C  # PRINT SCREEN key
VK_INSERT = 0x2D  # INS key
VK_DELETE = 0x2E  # DEL key
VK_HELP = 0x2F  # HELP key
VK_NUMPAD0 = 0x60  # Numeric keypad 0 key
VK_NUMPAD1 = 0x61  # Numeric keypad 1 key
VK_NUMPAD2 = 0x62  # Numeric keypad 2 key
VK_NUMPAD3 = 0x63  # Numeric keypad 3 key
VK_NUMPAD4 = 0x64  # Numeric keypad 4 key
VK_NUMPAD5 = 0x65  # Numeric keypad 5 key
VK_NUMPAD6 = 0x66  # Numeric keypad 6 key
VK_NUMPAD7 = 0x67  # Numeric keypad 7 key
VK_NUMPAD8 = 0x68  # Numeric keypad 8 key
VK_NUMPAD9 = 0x69  # Numeric keypad 9 key
VK_SEPARATOR = 0x6C  # Separator key
VK_SUBTRACT = 0x6D  # Subtract key
VK_DECIMAL = 0x6E  # Decimal key
VK_DIVIDE = 0x6F  # Divide key
VK_F1 = 0x70  # F1 key
VK_F2 = 0x71  # F2 key
VK_F3 = 0x72  # F3 key
VK_F4 = 0x73  # F4 key
VK_F5 = 0x74  # F5 key
VK_F6 = 0x75  # F6 key
VK_F7 = 0x76  # F7 key
VK_F8 = 0x77  # F8 key
VK_F9 = 0x78  # F9 key
VK_F10 = 0x79  # F10 key
VK_F11 = 0x7A  # F11 key
VK_F12 = 0x7B  # F12 key
VK_F13 = 0x7C  # F13 key
VK_F14 = 0x7D  # F14 key
VK_F15 = 0x7E  # F15 key
VK_F16 = 0x7F  # F16 key
VK_F17 = 0x80  # H F17 key
VK_F18 = 0x81  # H F18 key
VK_F19 = 0x82  # H F19 key
VK_F20 = 0x83  # H F20 key
VK_F21 = 0x84  # H F21 key
VK_F22 = 0x85  # H F22 key
VK_F23 = 0x86  # H F23 key
VK_F24 = 0x87  # H F24 key
VK_NUMLOCK = 0x90  # NUM LOCK key
VK_SCROLL = 0x91  # SCROLL LOCK key
VK_LSHIFT = 0xA0  # Left SHIFT key
VK_RSHIFT = 0xA1  # Right SHIFT key
VK_LCONTROL = 0xA2  # Left CONTROL key
VK_RCONTROL = 0xA3  # Right CONTROL key
VK_LMENU = 0xA4  # Left MENU key
VK_RMENU = 0xA5  # Right MENU key
VK_PLAY = 0xFA  # Play key
VK_ZOOM = 0xFB  # Zoom key
WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008


class GlobalHotkeyManagerWin(GlobalHotkeyManagerBase):
    _TranslateMessage = ctypes.WINFUNCTYPE(BOOL, POINTER(MSG))
    _TranslateMessageReal = None

    _qt_key_to_vk = {
        Qt.Key_Escape: VK_ESCAPE, Qt.Key_Tab: VK_TAB, Qt.Key_Backtab: VK_TAB,
        Qt.Key_Backspace: VK_BACK,
        Qt.Key_Return: VK_RETURN, Qt.Key_Enter: VK_RETURN,
        Qt.Key_Insert: VK_INSERT, Qt.Key_Delete: VK_DELETE,
        Qt.Key_Pause: VK_PAUSE, Qt.Key_Print: VK_SNAPSHOT,
        Qt.Key_Clear: VK_CLEAR, Qt.Key_Home: VK_HOME,
        Qt.Key_End: VK_END, Qt.Key_Left: VK_LEFT, Qt.Key_Up: VK_UP,
        Qt.Key_Right: VK_RIGHT, Qt.Key_Down: VK_DOWN,
        Qt.Key_PageUp: VK_PRIOR, Qt.Key_PageDown: VK_NEXT,
        Qt.Key_F1: VK_F1, Qt.Key_F2: VK_F2, Qt.Key_F3: VK_F3, Qt.Key_F4: VK_F4,
        Qt.Key_F5: VK_F5, Qt.Key_F6: VK_F6,
        Qt.Key_F7: VK_F7, Qt.Key_F8: VK_F8, Qt.Key_F9: VK_F9,
        Qt.Key_F10: VK_F10, Qt.Key_F11: VK_F11,
        Qt.Key_F12: VK_F12, Qt.Key_F13: VK_F13, Qt.Key_F14: VK_F14,
        Qt.Key_F15: VK_F15, Qt.Key_F16: VK_F16,
        Qt.Key_F17: VK_F17, Qt.Key_F18: VK_F18, Qt.Key_F19: VK_F19,
        Qt.Key_F20: VK_F20, Qt.Key_F21: VK_F21,
        Qt.Key_F22: VK_F22, Qt.Key_F23: VK_F23, Qt.Key_F24: VK_F24,
        Qt.Key_Space: VK_SPACE,
        # Qt.Key_Asterisk: VK_MULTIPLY,
        # Qt.Key_Plus: VK_ADD,
        Qt.Key_Comma: VK_SEPARATOR, Qt.Key_Minus: VK_SUBTRACT,
        Qt.Key_Slash: VK_DIVIDE,
        # Qt.Key_MediaNext: VK_MEDIA_NEXT_TRACK,
        # Qt.Key_MediaPrevious: VK_MEDIA_PREV_TRACK,
        # Qt.Key_MediaPlay: VK_MEDIA_PLAY_PAUSE,
        # Qt.Key_MediaStop: VK_MEDIA_STOP,
        # couldn't find those in VK_*
        # Qt.Key_MediaLast:
        # Qt.Key_MediaRecord:
        # Qt.Key_VolumeDown: VK_VOLUME_DOWN,
        # Qt.Key_VolumeUp: VK_VOLUME_UP,
        # Qt.Key_VolumeMute: VK_VOLUME_MUTE,
    }

    _qt_key_numbers = [getattr(Qt, 'Key_{}'.format(i)) for i in range(10)]
    _qt_key_letters = [getattr(Qt, 'Key_{}'.format(chr(ord('A') + i))) for i in
                       range(ord('Z') - ord('A'))]

    def __init__(self):
        GlobalHotkeyManagerBase.__init__(self)
        # Believe it or not - hooking TranslateMessage() is more stable than
        # using windows hooks.
        self._translate_message_hook_ref = self._TranslateMessage(
            self._translate_message_hook)
        self._TranslateMessageReal = self._TranslateMessage(
            hotpatch(ctypes.windll.user32.TranslateMessage,
                     self._translate_message_hook_ref)
        )

    def _translate_message_hook(self, pmsg):
        msg = pmsg.contents
        if msg.message == WM_HOTKEY:
            keycode = (msg.lParam >> 16) & 0xFFFF
            modifiers = msg.lParam & 0xFFFF
            key = (keycode, modifiers)
            if key in self.shortcuts:
                QTimer.singleShot(0, self.shortcuts[key])
                return False

        return self._TranslateMessageReal(pmsg)

    def destroy(self):
        unhotpatch(ctypes.windll.user32.TranslateMessage)

    def __del__(self):
        self.destroy()

    def _native_modifiers(self, modifiers):
        native = 0
        if modifiers & Qt.ShiftModifier:
            native |= MOD_SHIFT
        if modifiers & Qt.ControlModifier:
            native |= MOD_CONTROL
        if modifiers & Qt.AltModifier:
            native |= MOD_ALT
        if modifiers & Qt.MetaModifier:
            native |= MOD_WIN
        return native

    def _native_keycode(self, key):
        if key in self._qt_key_to_vk:
            return self._qt_key_to_vk[key]
        elif key in self._qt_key_numbers:
            return key
        elif key in self._qt_key_letters:
            return key
        return 0

    @staticmethod
    def _unwrap_window_id(window_id):
        try:
            return int(window_id)
        except:
            ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
            ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]
            return int(ctypes.pythonapi.PyCObject_AsVoidPtr(window_id))

    def _register_shortcut(self, receiver, native_key, native_mods, window_id):
        result = ctypes.windll.user32.RegisterHotKey(
            self._unwrap_window_id(window_id),
            int(native_mods) ^ int(native_key),
            native_mods, int(native_key)
        )
        if result:
            self.shortcuts[(native_key, native_mods)] = receiver

        return result

    def _unregister_shortcut(self, native_key, native_mods, window_id):
        result = ctypes.windll.user32.UnregisterHotKey(
            self._unwrap_window_id(window_id),
            int(native_mods) ^ int(native_key)
        )
        try:
            del self.shortcuts[(native_key, native_mods)]
        except KeyError:
            pass

        return result
