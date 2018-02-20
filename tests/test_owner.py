import pytest
from PySide.QtGui import QMainWindow, QWidget

from clipmanager import owner


@pytest.mark.skip(reason='BUG: get_active_window_id() fails.')
def test_owner(qtbot):
    window = QMainWindow()
    window.setWindowTitle('owner-package-test')
    window.setCentralWidget(QWidget())
    window.show()

    qtbot.addWidget(window)
    qtbot.waitForWindowShown(window)

    current_app = owner.initialize()
    window_names = current_app()

    assert len(window_names) > 0
    assert 'owner-package-test' in window_names
