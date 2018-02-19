import pytest
from PySide.QtCore import QMimeData, Qt
from PySide.QtGui import QDialogButtonBox

from clipmanager.settings import Settings
from clipmanager.ui.dialogs.about import AboutDialog
from clipmanager.ui.dialogs.preview import PreviewDialog
from clipmanager.ui.dialogs.settings import SettingsDialog


@pytest.fixture()
def about_dialog(qtbot):
    dialog = AboutDialog()
    dialog.show()
    qtbot.addWidget(dialog)
    return qtbot, dialog


@pytest.fixture()
def preview_dialog(qtbot):
    mime_data = QMimeData()
    mime_data.setData('text/plain', 'text')
    dialog = PreviewDialog(mime_data)
    dialog.show()
    qtbot.addWidget(dialog)
    return qtbot, dialog


@pytest.fixture()
def settings_dialog(qtbot):
    dialog = SettingsDialog()
    dialog.show()
    qtbot.addWidget(dialog)
    return qtbot, dialog


class TestAboutDialog:
    def test_close(self, about_dialog):
        qtbot, dialog = about_dialog
        with qtbot.waitSignal(dialog.accepted, 1000, True):
            button = dialog.button_box.button(QDialogButtonBox.Close)
            qtbot.mouseClick(button, Qt.LeftButton)


class TestPreviewDialog:
    def test_close(self, preview_dialog):
        qtbot, dialog = preview_dialog
        with qtbot.waitSignal(dialog.accepted, 1000, True):
            button = dialog.button_box.button(QDialogButtonBox.Close)
            qtbot.mouseClick(button, Qt.LeftButton)


class TestSettingsDialog:
    def setup(self):
        self.settings = Settings()
        self.settings.clear()

    @staticmethod
    def _cancel(qtbot, dialog):
        button = dialog.button_box.button(QDialogButtonBox.Cancel)
        qtbot.mouseClick(button, Qt.LeftButton)

    def test_save(self, settings_dialog):
        qtbot, dialog = settings_dialog
        with qtbot.waitSignal(dialog.accepted, 1000, True):
            button = dialog.button_box.button(QDialogButtonBox.Save)
            qtbot.mouseClick(button, Qt.LeftButton)

    def test_cancel(self, settings_dialog):
        qtbot, dialog = settings_dialog
        with qtbot.waitSignal(dialog.rejected, 1000, True):
            button = dialog.button_box.button(QDialogButtonBox.Cancel)
            qtbot.mouseClick(button, Qt.LeftButton)

    def test_valid_global_shortcut(self, settings_dialog):
        qtbot, dialog = settings_dialog
        qtbot.keyPress(dialog.key_combo_edit, 'H', Qt.ControlModifier)
        assert dialog.key_combo_edit.text().lower() == 'ctrl+h'

    def test_invalid_global_shortcut(self, settings_dialog):
        qtbot, dialog = settings_dialog
        qtbot.keyPress(dialog.key_combo_edit, Qt.Key_F5, Qt.NoModifier)
        assert dialog.key_combo_edit.text().lower() == 'ctrl+shift+h'  # default

    def test_exclude_application(self, settings_dialog):
        qtbot, dialog = settings_dialog

        dialog.exclude_edit.setText('app1')
        button = dialog.button_box.button(QDialogButtonBox.Save)
        qtbot.mouseClick(button, Qt.LeftButton)
        assert self.settings.get_exclude() == 'app1;'

        dialog.exclude_edit.setText('app1;app2;')
        button = dialog.button_box.button(QDialogButtonBox.Save)
        qtbot.mouseClick(button, Qt.LeftButton)
        assert self.settings.get_exclude() == 'app1;app2;'
