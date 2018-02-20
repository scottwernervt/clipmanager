import logging
import subprocess

from Xlib import X, XK
from Xlib.display import Display
from Xlib.error import DisplayError, XError
from Xlib.protocol import event

logger = logging.getLogger(__name__)

PASTE_KEY = "v"


def _get_keycode(key, display):
    keysym = XK.string_to_keysym(key)
    keycode = display.keysym_to_keycode(keysym)
    return keycode


def _paste_x11():
    display = Display()
    root = display.screen().root
    window = display.get_input_focus().focus

    window.grab_keyboard(False, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)
    display.flush()

    keycode = _get_keycode(PASTE_KEY, display)

    key_press = event.KeyPress(detail=keycode,
                               time=X.CurrentTime,
                               root=root,
                               window=window,
                               child=X.NONE,
                               root_x=0,
                               root_y=0,
                               event_x=0,
                               event_y=0,
                               state=X.ControlMask,
                               same_screen=1)
    key_release = event.KeyRelease(detail=keycode,
                                   time=X.CurrentTime,
                                   root=root,
                                   window=window,
                                   child=X.NONE,
                                   root_x=0,
                                   root_y=0,
                                   event_x=0,
                                   event_y=0,
                                   state=X.ControlMask,
                                   same_screen=1)

    window.send_event(key_press)
    window.send_event(key_release)
    display.ungrab_keyboard(X.CurrentTime)

    display.flush()
    display.close()
    return True


def _paste_xdotool():
    cmd = ['xdotool', 'key', '--delay', '100', 'ctrl+v']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, close_fds=True)
    return p.returncode


def paste_action():
    """Execute paste key shortcut, CTRL+V.

    If X11 fails, fallback to xdotool.

    :return: None
    :rtype: None
    """
    try:
        _paste_x11()
    except (DisplayError, XError) as e:
        logger.exception(e)
        _paste_xdotool()
