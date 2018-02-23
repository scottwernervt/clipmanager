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
        self.setWindowIcon(get_icon('clipmanager.ico'))
        self.setAttribute(Qt.WA_DeleteOnClose)

        app_name = QCoreApplication.applicationName()
        app_version = QCoreApplication.applicationVersion()

        app_homepage = QLabel('<a href="{0}">{0}</a>'.format(__url__))
        app_homepage.setTextFormat(Qt.RichText)
        app_homepage.setTextInteractionFlags(Qt.TextBrowserInteraction)
        app_homepage.setOpenExternalLinks(True)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.setFocus()

        layout = QGridLayout()
        layout.addWidget(QLabel('Name:'), 0, 0)
        layout.addWidget(QLabel(app_name), 0, 1)
        layout.addWidget(QLabel('Version:'), 1, 0)
        layout.addWidget(QLabel(app_version), 1, 1)
        layout.addWidget(QLabel('License:'), 2, 0)
        layout.addWidget(QLabel(__license__), 2, 1)
        layout.addWidget(QLabel('Homepage:'), 4, 0)
        layout.addWidget(app_homepage, 4, 1)
        layout.addWidget(self.button_box, 5, 0, 1, 4)
        self.setLayout(layout)

        self.button_box.rejected.connect(self.close)

    @Slot()
    def close(self):
        """Close dialog.

        :return: None
        :rtype: None
        """
        self.done(True)
