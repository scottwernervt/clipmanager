import logging

from PySide.QtCore import QMimeData, QObject, Signal, Slot
from PySide.QtGui import QApplication, QClipboard

logger = logging.getLogger(__name__)


class ClipboardManager(QObject):
    """Handles communication between all clipboards and main window.

    Source: http://bazaar.launchpad.net/~glipper-drivers/glipper/Clipboards.py
    """
    new_item = Signal(QMimeData)

    def __init__(self, parent=None):
        super(ClipboardManager, self).__init__(parent)

        self.primary_clipboard = Clipboard(QApplication.clipboard(),
                                           self.new_item)

    def get_primary_clipboard_text(self):
        """Get primary clipboard contents.

        :return: Current clipboard contents.
        :rtype: QMimeData
        """
        return self.primary_clipboard.get_text()

    def set_text(self, mime_data):
        """Set clipboard contents.

        :param mime_data: Data to set to global clipboard.
        :type mime_data: QMimeData

        :return: None
        :rtype: None
        """
        self.primary_clipboard.set_text(mime_data)
        self.new_item.emit(mime_data)

    def clear_text(self):
        self.primary_clipboard.clear_text()


class Clipboard(QObject):
    """Monitor's clipboard for changes.

    :param clipboard: Clipboard reference.
    :type clipboard: QClipboard

    :param callback: Function to call on content change.
    :type callback: func

    :param mode:
    :type mode: QClipboard.Mode.Clipboard
    """

    def __init__(self, clipboard, callback, mode=QClipboard.Clipboard):
        super(Clipboard, self).__init__()

        self.clipboard = clipboard
        self.callback = callback
        self.mode = mode

        self.clipboard.dataChanged.connect(self.on_data_changed)

    def get_text(self):
        """Get clipboard contents.

        :return: Current clipboard contents.
        :rtype: QMimeData
        """
        return self.clipboard.mimeData(self.mode)

    def set_text(self, mime_data):
        """Set clipboard contents.

        :param mime_data: Data to set to global clipboard.
        :type mime_data: QMimeData

        :return: None
        :rtype: None
        """
        self.clipboard.setMimeData(mime_data, self.mode)

    def clear_text(self):
        """Clear clipboard contents.

        :return: None
        :rtype: None
        """
        self.clipboard.clear(mode=self.mode)

    @Slot()
    def on_data_changed(self):
        """Add new clipboard item using callback.

        :return: None
        :rtype: None
        """
        self.callback.emit(self.get_text())
