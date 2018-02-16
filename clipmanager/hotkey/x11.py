"""
Source: https://github.com/rokups/paste2box
License: GNU General Public License v3.0
"""

from PySide.QtCore import QObject, QThread, QTimer, Qt, Signal
from PySide.QtGui import QApplication, QKeySequence
from Xlib import X, XK
from Xlib.display import Display
from Xlib.ext import record
from Xlib.protocol import rq

from clipmanager.hotkey.base import GlobalHotkeyManagerBase


class X11EventPoller(QObject):
    keyPressed = Signal(object, object)

    def __init__(self):
        QObject.__init__(self)
        self._display = Display()
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.start()

    def start(self):
        QTimer.singleShot(0, self.run)

    def run(self):
        ctx = self._display.record_create_context(
            0,
            [record.CurrentClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (
                    0, 0, 0, 0),
                'ext_replies': (
                    0, 0, 0, 0),
                'delivered_events': (
                    0, 0),
                'device_events': (
                    X.KeyPress,
                    X.KeyRelease),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }]
        )
        self._display.record_enable_context(ctx, self._record_callback)
        self._display.record_free_context(ctx)

    def _record_callback(self, reply):
        QApplication.processEvents()
        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            # received swapped protocol data, cowardly ignored
            return
        if not len(reply.data) or reply.data[0] < 2:
            # not an event
            return

        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(
                data,
                self._display.display,
                None, None)
            self.keyPressed.emit(event, data)

    def destroy(self):
        # TODO: This thread state must be current when releasing.
        self._thread.terminate()
        self._thread.wait()

    def __del__(self):
        self.destroy()


class GlobalHotkeyManagerX11(GlobalHotkeyManagerBase):
    def __init__(self):
        self._text_to_native = {
            '-': 'minus',
            '+': 'plus',
            '=': 'equal',
            '[': 'bracketleft',
            ']': 'bracketright',
            '|': 'bar',
            ';': 'semicolon',
            '\'': 'quoteright',
            ',': 'comma',
            '.': 'period',
            '/': 'slash',
            '\\': 'backslash',
            '`': 'asciitilde',
        }
        GlobalHotkeyManagerBase.__init__(self)

        self._error = False
        self._display = Display()
        self._poller = X11EventPoller()
        self._poller.keyPressed.connect(self.x11_event)
        self._poller.start()

    def destroy(self):
        self._poller.destroy()

    # noinspection PyUnusedLocal
    def x11_event(self, event, data):
        if event.type == X.KeyPress:
            key = (event.detail, int(event.state) & (
                    X.ShiftMask | X.ControlMask | X.Mod1Mask | X.Mod4Mask))
            if key in self.shortcuts:
                # noinspection PyCallByClass,PyTypeChecker
                QTimer.singleShot(0, self.shortcuts[key])
        return False

    def _native_modifiers(self, modifiers):
        # ShiftMask, LockMask, ControlMask, Mod1Mask, Mod2Mask, Mod3Mask,
        # Mod4Mask, and Mod5Mask
        native = 0
        modifiers = int(modifiers)

        if modifiers & Qt.ShiftModifier:
            native |= X.ShiftMask
        if modifiers & Qt.ControlModifier:
            native |= X.ControlMask
        if modifiers & Qt.AltModifier:
            native |= X.Mod1Mask
        if modifiers & Qt.MetaModifier:
            native |= X.Mod4Mask

        # TODO: resolve these?
        # if (modifiers & Qt.MetaModifier)
        # if (modifiers & Qt.KeypadModifier)
        # if (modifiers & Qt.GroupSwitchModifier)
        return native

    def _native_keycode(self, key):
        keysym = QKeySequence(key).toString()
        if keysym in self._text_to_native:
            keysym = self._text_to_native[keysym]
        return self._display.keysym_to_keycode(XK.string_to_keysym(keysym))

    # noinspection PyUnusedLocal
    def _on_error(self, e, data):
        if e.code in (X.BadAccess, X.BadValue, X.BadWindow):
            if e.major_opcode in (33, 34):  # X_GrabKey, X_UngrabKey
                self._error = True
        return 0

    def _register_shortcut(self, receiver, native_key, native_mods, winid=None):
        window = self._display.screen().root
        self._error = False

        window.grab_key(native_key, native_mods, True, X.GrabModeAsync,
                        X.GrabModeAsync, self._on_error)
        self._display.sync()

        if not self._error:
            self.shortcuts[(native_key, native_mods)] = receiver

        return not self._error

    def _unregister_shortcut(self, native_key, native_mods, window_id):
        display = Display()
        window = display.screen().root
        self._error = False

        window.ungrab_key(native_key, native_mods, self._on_error)
        display.sync()

        try:
            del self.shortcuts[(native_key, native_mods)]
        except KeyError:
            pass

        return not self._error
