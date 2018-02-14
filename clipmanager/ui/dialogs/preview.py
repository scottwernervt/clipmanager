from PySide.QtCore import QSize, Qt
from PySide.QtGui import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QIcon,
    QTextCursor,
    QTextEdit,
)
from PySide.QtWebKit import QWebSettings, QWebView

from clipmanager.ui.icons import resource_filename


class PreviewDialog(QDialog):
    """Display preview of item."""

    def __init__(self, parent=None):
        super(PreviewDialog, self).__init__(parent)
        self.parent = parent

        self.setWindowIcon(QIcon(resource_filename('icons/clipmanager.ico')))
        self.setWindowTitle('Preview')
        self.resize(QSize(500, 300))
        self.setAttribute(Qt.WA_DeleteOnClose)

    def setup_ui(self, mime_data):
        """Preview display is determined by mime format.

        :param mime_data:
        :type mime_data: QMimeData

        :return: None
        :rtype: None
        """
        # if mime_data.hasImage():
        #     pass
        #     image = QImage(mime_data.imageData())
        #     # print type(image)
        #     doc = QLabel()
        #     pixmap = QPixmap.fromImage(image)
        #     doc.setPixmap(pixmap)

        # Allow images to be loaded if html
        if mime_data.hasHtml():
            self.doc = QWebView(self)
            self.doc.settings().setAttribute(
                QWebSettings.LocalContentCanAccessRemoteUrls, True)
            self.doc.settings().setAttribute(
                QWebSettings.LocalContentCanAccessFileUrls, True)
            self.doc.setHtml(mime_data.html())
        else:
            self.doc = QTextEdit(self)

            if mime_data.hasUrls():
                text = 'Copied File(s): '
                for url in mime_data.urls():
                    text += url.toLocalFile() + '\n'
                self.doc.setPlainText(text)

            elif self.doc.canInsertFromMimeData(mime_data):
                self.doc.insertFromMimeData(mime_data)

            else:
                self.doc.setPlainText(('Unknown error has occurred.\n'
                                       'Formats: %s' % mime_data.formats()))

            # Move cursor to top causing scrollbar to move to top
            self.doc.moveCursor(QTextCursor.Start)
            self.doc.ensureCursorVisible()
            self.doc.setReadOnly(True)  # Do not support editing data yet

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.setFocus()

        layout = QGridLayout(self)
        layout.addWidget(self.doc, 0, 0)
        layout.addWidget(button_box, 1, 0)
        self.setLayout(layout)

        button_box.rejected.connect(self.close)

    def close(self):
        """Close dialog.

        :return: None
        :rtype: None
        """
        self.done(True)
