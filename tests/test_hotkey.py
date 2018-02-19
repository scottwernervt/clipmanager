import pytest
from PySide.QtCore import Qt
from PySide.QtGui import QMainWindow

from clipmanager import hotkey


@pytest.fixture()
def main_window(qtbot):
    mw = QMainWindow()
    mw.showMaximized()

    qtbot.addWidget(mw)
    qtbot.waitForWindowShown(mw)

    hk = hotkey.initialize()
    yield qtbot, mw, hk
    hk.unregister(winid=mw.winId())


def callback():
    return True


class TestGlobalHotKey:
    def test_register(self, main_window):
        qtbot, mw, hk = main_window
        assert hk.register('Ctrl+Return', callback, mw.winId())
        qtbot.keyPress(mw, Qt.Key_Return, modifier=Qt.ControlModifier)

    def test_unregister(self, main_window):
        qtbot, mw, hk = main_window
        hk.unregister(winid=mw.winId())
