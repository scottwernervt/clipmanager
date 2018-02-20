import pytest
from PySide.QtGui import QCloseEvent, QSystemTrayIcon

from clipmanager.ui.mainwindow import MainWidget, MainWindow

pytestmark = pytest.mark.skip('MainWindow tests lock up.')


@pytest.fixture()
def main_window(qtbot):
    mw = MainWindow()
    mw.show()
    qtbot.addWidget(mw)
    return qtbot, mw


@pytest.fixture()
def main_widget(qtbot):
    mw = MainWidget()
    mw.show()
    qtbot.addWidget(mw)

    return qtbot, mw


class TestMainWindow:
    def test_close_event(self, main_window):
        qtbot, window = main_window
        window.show()
        event = QCloseEvent()
        window.closeEvent(event)
        assert not window.isVisible()

    def test_system_tray_icon(self, main_window):
        qtbot, window = main_window
        window.hide()
        window.system_tray_activate(QSystemTrayIcon.Trigger)
        assert window.isVisible()
