from PySide.QtCore import QSize, Qt
from PySide.QtGui import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QTextCursor,
    QTextEdit,
)
from PySide.QtWebKit import QWebSettings, QWebView

from clipmanager.ui.icons import get_icon


class PreviewDialog(QDialog):
    """Display preview of item."""

    def __init__(self, mime_data, parent=None):
        """Preview display is determined by mime format.

        :param mime_data:
        :type mime_data: QMimeData

        :param parent:
        :type parent:
        """
        super(PreviewDialog, self).__init__(parent)

        self.parent = parent

        self.setWindowIcon(get_icon('clipmanager.ico'))
        self.setWindowTitle('Preview')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(QSize(500, 300))

        if mime_data.hasHtml():
            doc = QWebView(self)
            doc.settings().setAttribute(
                QWebSettings.LocalContentCanAccessRemoteUrls,
                True
            )
            doc.settings().setAttribute(
                QWebSettings.LocalContentCanAccessFileUrls,
                True
            )
            html = mime_data.html()
            doc.setHtml(html)
        else:
            doc = QTextEdit(self)

            if mime_data.hasUrls():
                text = 'Copied File(s): '
                for url in mime_data.urls():
                    text += url.toLocalFile() + '\n'
                doc.setPlainText(text)
            elif doc.canInsertFromMimeData(mime_data):
                doc.insertFromMimeData(mime_data)
            else:
                doc.setPlainText(
                    'Invalid data formats: %s' % ','.join(mime_data.formats())
                )

            # Move cursor to top causing scrollbar to move to top
            doc.moveCursor(QTextCursor.Start)
            doc.ensureCursorVisible()
            doc.setReadOnly(True)  # Do not support editing data yet

        close_button_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_button_box.setFocus()

        layout = QGridLayout(self)

        layout.addWidget(doc, 0, 0)
        layout.addWidget(close_button_box, 1, 0)

        self.setLayout(layout)

        close_button_box.rejected.connect(self.close)

    def close(self):
        """Close dialog.

        :return: None
        :rtype: None
        """
        self.done(True)
