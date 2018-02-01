#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
import logging
import re
from ctypes import wintypes

import win32con
from PySide import QtCore

logging.getLogger(__name__)

# http://msdn.microsoft.com/en-us/library/windows/desktop/ms646309(v=vs.85).aspx
WIN_MODIFIERS = {
    'CTRL': win32con.MOD_CONTROL,
    'ALT': win32con.MOD_ALT,
    'SHIFT': win32con.MOD_SHIFT,
    'SUPER': win32con.MOD_WIN,
}

# http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731(v=vs.85).aspx
WIN_VIRTUAL_KEYS = {
    '`': 0xC0,
    '~': 0xC0,
}


class Binder(QtCore.QObject):
    """Global handler for binding and unbinding key strokes and their actions.

    Class handles platform specific commands.
    """

    def __init__(self, action, parent=None):
        super(Binder, self).__init__(parent)
        self.action = action
        self.parent = parent

        self.monitor_thread = None

    def bind(self, key_seq, action):
        """Bind global hot key to action.

        Args:
            key_seq (str): <CTRL><ALT>H
            action (bound method): Method to execute when key stroke is
                executed.
        """
        logging.info('Binding key seq %s to : %s' % (key_seq, action))

        self.monitor_thread = _Thread(self)
        result = self.monitor_thread.bind(key_seq)

        if result:
            logging.info('Binding successful')
        else:
            logging.error('Binding failed')

        self.monitor_thread.start()

        self.connect(self.monitor_thread,
                     QtCore.SIGNAL('action-trigger()'), action)

        return result

    def unbind(self, key_seq):
        """Unbind global hot key.

        Args:
            key_seq (str): <CTRL><ALT>H
        """
        logging.info('Unbinding key seq: %s' % key_seq)

        self.monitor_thread.unregister_hot_key()
        self.monitor_thread.terminate()
        self.monitor_thread.wait()

        self.monitor_thread = None


class _Thread(QtCore.QThread):
    """Monitor window key stroke events.

    Todo:
        http://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/

    References:
        http://svn.gna.org/svn/congabonga/trunk/lib/winhotkeys.py
        https://github.com/Xifax/tuci/blob/master/src/hotkeys.py
    """

    def __init__(self, parent=None):
        super(_Thread, self).__init__(parent)
        self.parent = None

        self.key = None
        self.byref = ctypes.byref
        self.user32 = ctypes.windll.user32

        self.id = 1
        self.modifiers = 0
        self.vk = 0

    def bind(self, key_seq, action=None):
        """
        Args:
            key_seq (str): <CTRL><ALT>H
            action (bound method): Method to execute when key stroke is
                executed.
        """
        p = re.compile('\<(.*?)\>')
        modifiers = p.findall(key_seq)
        logging.info('Modifiers: %s' % modifiers)

        for modifier in modifiers:
            try:
                self.modifiers += WIN_MODIFIERS[modifier.upper()]
            except KeyError as err:
                logging.warn(err)
                return False

        self.key = key_seq[-1].upper()

        # Handle virtual keys (non-alphabet) like `~
        if self.key in WIN_VIRTUAL_KEYS:
            self.vk = WIN_VIRTUAL_KEYS[self.key]
        else:
            self.vk = ord(self.key)

        logging.info('Key: %s' % self.key)
        return True

    def register_hot_key(self):
        if not self.user32.RegisterHotKey(None, self.id, self.modifiers
                , self.vk):
            logging.error('Failed to register.')
            return False
        else:
            logging.info('Registered.')
            return True

    def unregister_hot_key(self):
        logging.info('Unregistering key...')
        self.user32.UnregisterHotKey(None, self.id)

    def run(self):
        logging.debug('Running...')
        self.register_hot_key()

        try:
            msg = wintypes.MSG()
            while self.isRunning():
                if self.user32.GetMessageA(self.byref(msg), None, 0, 0) != 0:
                    if msg.message == win32con.WM_HOTKEY:
                        self.emit(QtCore.SIGNAL('action-trigger()'))

            self.user32.TranslateMessage(self.byref(msg))
            self.user32.DispatchMessageA(self.byref(msg))

            self.unregister_hot_key()

        except Exception as err:
            logging.error(err)

    def __del__(self):
        self.user32.TranslateMessage(self.byref(msg))
        self.user32.DispatchMessageA(self.byref(msg))
        self.unregister_hot_key()
        self.exit()
