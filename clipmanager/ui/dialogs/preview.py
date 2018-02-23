from PySide.QtCore import QSize, Qt, Slot
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
                    'Invalid data formats: {}'.format(
                        ','.join(mime_data.formats())
                        )
                )

            doc.moveCursor(QTextCursor.Start)  # scroll to top
            doc.ensureCursorVisible()
            doc.setReadOnly(True)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.setFocus()

        layout = QGridLayout(self)
        layout.addWidget(doc, 0, 0)
        layout.addWidget(self.button_box, 1, 0)
        self.setLayout(layout)

        self.button_box.rejected.connect(self.close)

    @Slot()
    def close(self):
        """Close dialog.

        :return: None
        :rtype: None
        """
        self.done(True)
