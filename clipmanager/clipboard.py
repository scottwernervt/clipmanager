import logging

from PySide.QtCore import QObject, SIGNAL, Slot
from PySide.QtGui import QApplication, QClipboard

logger = logging.getLogger(__name__)


class ClipboardManager(QObject):
    """Handles communication between all clipboards and main window.

    Source: http://bazaar.launchpad.net/~glipper-drivers/glipper/Clipboards.py
    """

    def __init__(self, parent=None):
        super(ClipboardManager, self).__init__(parent)

        self.primary_clipboard = Clipboard(QApplication.clipboard(),
                                           self.emit_new_item,
                                           QClipboard.Clipboard)

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
        self.emit_new_item(mime_data)

    def clear_text(self):
        self.primary_clipboard.clear_text()

    def emit_new_item(self, mime_data):
        """Emits new clipboard contents to main window.

        :param mime_data:
        :type mime_data: QMimeData

        :return: None
        :rtype: None
        """
        self.emit(SIGNAL('newItem(QMimeData)'), mime_data)


class Clipboard(QObject):
    """Monitor's clipboard for changes.

    :param clipboard: Clipboard reference.
    :type clipboard: QClipboard

    :param new_item_callback: Function to call on content change.
    :type new_item_callback: pyfunc

    :param mode:
    :type mode: QClipboard.Mode.Clipboard
    """

    def __init__(self, clipboard, new_item_callback, mode):
        super(Clipboard, self).__init__()

        self.clipboard = clipboard
        self.new_item_callback = new_item_callback
        self.mode = mode

        self.connect(self.clipboard, SIGNAL('dataChanged()'),
                     self.on_data_changed)

        self.connect(self.clipboard, SIGNAL('ownerDestroyed()'),
                     self.on_owner_change)

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
    def on_owner_change(self):
        """Handle X11 ownership destruction.

        If you change the selection within a window, X11 will only notify the
        owner and the previous owner of the change, i.e. it will not notify all
        applications that the selection or clipboard data emit_new_item.

        :return: None
        :rtype: None
        """
        self.new_item_callback(self.contents)

    @Slot()
    def on_data_changed(self):
        """Add new clipboard item using callback.

        :return: None
        :rtype: None
        """
        self.new_item_callback(self.get_text())
