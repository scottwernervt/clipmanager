from PySide.QtGui import QMainWindow

from clipmanager import owner


def test_owner(qtbot):
    window = QMainWindow()
    window.setWindowTitle('owner-package-test')
    window.showMaximized()

    qtbot.addWidget(window)
    qtbot.waitForWindowShown(window)

    current_app = owner.initialize()
    window_names = current_app()

    assert len(window_names) > 0
    assert 'owner-package-test' in window_names
