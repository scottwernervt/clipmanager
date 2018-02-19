import pytest
from PySide.QtCore import QMimeData

from clipmanager.clipboard import ClipboardManager


@pytest.fixture(scope='function')
def clipboard_manager():
    cbm = ClipboardManager()
    yield cbm
    cbm.clear_text()


@pytest.fixture(scope='function')
def text_data():
    text = QMimeData()
    text.setText('test')
    return text


@pytest.fixture(scope='function')
def html_data():
    html = QMimeData()
    html.setHtml('<h1>test</h1>')
    return html


class TestClipboardManager:
    def test_set_text(self, clipboard_manager, text_data):
        clipboard_manager.set_text(text_data)
        contents = clipboard_manager.get_primary_clipboard_text()
        assert contents.text() == text_data.text()

    def test_set_html(self, clipboard_manager, html_data):
        clipboard_manager.set_text(html_data)
        contents = clipboard_manager.get_primary_clipboard_text()
        assert contents.html() == html_data.html()

    def test_clear_text(self, clipboard_manager):
        clipboard_manager.clear_text()
        contents = clipboard_manager.get_primary_clipboard_text()
        assert not contents.text()

    def test_new_item_signal(self, qtbot, clipboard_manager):
        with qtbot.waitSignal(clipboard_manager.new_item, 1000, True):
            clipboard_manager.set_text(QMimeData())
