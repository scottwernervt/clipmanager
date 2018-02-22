from PySide.QtCore import QCoreApplication, Qt, Slot
from PySide.QtGui import QDialog, QDialogButtonBox, QGridLayout, QLabel

from clipmanager import __license__, __url__
from clipmanager.ui.icons import get_icon


class AboutDialog(QDialog):
    """About dialog that displays information about application."""

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        self.parent = parent

        self.setWindowTitle('About')
        self.setWindowIcon(get_icon('clipmanager'))
        self.setAttribute(Qt.WA_DeleteOnClose)

        app_name = QCoreApplication.applicationName()
        app_version = QCoreApplication.applicationVersion()

        app_url = QLabel('<a href="%s">%s</a>' % (__url__, __url__))
        app_url.setTextFormat(Qt.RichText)
        app_url.setTextInteractionFlags(Qt.TextBrowserInteraction)
        app_url.setOpenExternalLinks(True)

        icons_url = QLabel(
            '<a href="{0}">{0}</a>'.format(
                'https://github.com/horst3180/arc-icon-theme')
        )
        icons_url.setTextFormat(Qt.RichText)
        icons_url.setTextInteractionFlags(Qt.TextBrowserInteraction)
        icons_url.setOpenExternalLinks(True)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.setFocus()

        layout = QGridLayout()
        layout.addWidget(QLabel('Name:'), 0, 0)
        layout.addWidget(QLabel(app_name), 0, 1)
        layout.addWidget(QLabel('Version:'), 1, 0)
        layout.addWidget(QLabel(app_version), 1, 1)
        layout.addWidget(QLabel('License:'), 2, 0)
        layout.addWidget(QLabel(__license__), 2, 1)
        layout.addWidget(QLabel('Url:'), 4, 0)
        layout.addWidget(app_url, 4, 1)
        layout.addWidget(QLabel('Icons:'), 5, 0)
        layout.addWidget(icons_url, 5, 1)
        layout.addWidget(self.button_box, 6, 0, 1, 4)
        self.setLayout(layout)

        self.button_box.rejected.connect(self.close)

    @Slot()
    def close(self):
        """Close dialog.

        :return: None
        :rtype: None
        """
        self.done(True)
