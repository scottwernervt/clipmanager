import pytest

from clipmanager.ui.systemtray import SystemTrayIcon


@pytest.fixture()
def systemtray():
    tray = SystemTrayIcon()
    tray.show()
    return tray


class TestSystemTrayIcon:
    def test_is_visible(self, systemtray):
        assert systemtray.isVisible()
