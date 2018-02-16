from PySide.QtCore import QCoreApplication, Qt
from PySide.QtGui import QDialog, QDialogButtonBox, QGridLayout, QIcon, QLabel

from clipmanager import __license__
from clipmanager.ui.icons import get_icon


class AboutDialog(QDialog):
    """About dialog that displays information about application."""

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        self.parent = parent

        self.setWindowTitle('About')
        self.setWindowIcon(QIcon(get_icon('clipmanager.ico')))
        self.setAttribute(Qt.WA_DeleteOnClose)

        app_name = QCoreApplication.applicationName()
        app_version = QCoreApplication.applicationVersion()
        app_domain = QCoreApplication.organizationDomain()

        app_url = QLabel('<a href="%s">%s</a>' % (app_domain, app_domain))
        app_url.setTextFormat(Qt.RichText)
        app_url.setTextInteractionFlags(Qt.TextBrowserInteraction)
        app_url.setOpenExternalLinks(True)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)

        layout = QGridLayout()

        layout.addWidget(QLabel('Name:'), 0, 0)
        layout.addWidget(QLabel(app_name), 0, 1)
        layout.addWidget(QLabel('Version:'), 1, 0)
        layout.addWidget(QLabel(app_version), 1, 1)
        layout.addWidget(QLabel('License:'), 2, 0)
        layout.addWidget(QLabel(__license__), 2, 1)
        layout.addWidget(QLabel('Url:'), 4, 0)
        layout.addWidget(app_url, 4, 1)
        layout.addWidget(button_box, 5, 0, 1, 4)

        self.setLayout(layout)

        button_box.rejected.connect(self.close)

    def close(self):
        """Close dialog.

        :return: None
        :rtype: None
        """
        self.done(True)
