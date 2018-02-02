"""
Source: https://github.com/rokups/paste2box
License: GNU General Public License v3.0
"""

from PySide.QtCore import Qt, Signal
from PySide.QtGui import QKeySequence


class GlobalHotkeyManagerBase(object):
    keyPressed = Signal(int)
    keyReleased = Signal(int)

    def __init__(self):
        self.shortcuts = {}

    def register(self, sequence, callback, winid):
        if not isinstance(sequence, QKeySequence):
            sequence = QKeySequence(sequence)
        assert isinstance(sequence, QKeySequence), 'Invalid sequence type'
        k, m = self._sequence_to_native(sequence)
        return self._register_shortcut(callback, k, m, winid)

    def unregister(self, sequence=None, callback=None, winid=None):
        if sequence is not None:
            assert callback is not None, 'Invalid parameter'
            if isinstance(sequence, str):
                sequence = QKeySequence(sequence)
            assert isinstance(sequence, QKeySequence), 'Invalid sequence type'
            k, m = self._sequence_to_native(sequence)
            self._unregister_shortcut(k, m, winid)
        elif callback is not None:
            assert sequence is not None, 'Invalid parameter'
            for (k, m), cb in self.shortcuts.items():
                if callback == cb:
                    self._unregister_shortcut(k, m, winid)
        else:
            for (k, m), cb in self.shortcuts.copy().items():
                self._unregister_shortcut(k, m, winid)

    def _sequence_to_native(self, sequence):
        all_mods = int(Qt.ShiftModifier |
                       Qt.ControlModifier |
                       Qt.AltModifier |
                       Qt.MetaModifier)
        assert not sequence.isEmpty()
        key = Qt.Key((sequence[0] ^ all_mods) & sequence[0])
        mods = Qt.KeyboardModifiers(sequence[0] ^ int(key))
        return self._native_keycode(key), self._native_modifiers(mods)

    def _native_modifiers(self, modifiers):
        raise NotImplemented()

    def _native_keycode(self, key):
        raise NotImplemented()

    def _register_shortcut(self, receiver, native_key, native_mods, winid):
        raise NotImplemented()

    def _unregister_shortcut(self, native_key, native_mods, winid):
        raise NotImplemented()
