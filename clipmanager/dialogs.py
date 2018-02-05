import logging

from PySide.QtCore import QCoreApplication, QSize, Qt
from PySide.QtGui import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QIcon,
    QKeySequence,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QSpinBox,
    QTextCursor,
    QTextEdit,
    QVBoxLayout,
    QValidator,
)
from PySide.QtWebKit import QWebSettings, QWebView

from __init__ import __license__
from settings import settings
from utils import resource_filename

logging.getLogger(__name__)


def _check_state(state):
    """Toggle QCheckBox based on boolean state.

    Args:
        state (int/boolean): Checked or not checked.

    Returns:
        Qt.Checked/Qt.Unchecked
    """
    if state:
        return Qt.Checked
    else:
        return Qt.Unchecked


class PreviewDialog(QDialog):
    """Dialog to display model full contents.

    Todo:
        Allow user to edit data and save it back to database.
    """

    def __init__(self, parent=None):
        super(PreviewDialog, self).__init__(parent)
        self.parent = parent

        self.setWindowIcon(
            QIcon(resource_filename('icons/clipmanager.ico')))
        self.setWindowTitle('Preview')
        self.resize(QSize(500, 300))
        self.setAttribute(Qt.WA_DeleteOnClose)

    def setup_ui(self, mime_data):
        """Determine what to display based on mime data formats.

        If mime_data has html, then use QWebView to display content: tables,
        images, etc. If mime_data has plain text, then use QTextEdit to display
        contents.

        Args:
            mime_data: QMimeData
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
                self.doc.setPlainText(('Unknown error has occured.\n'
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

        button_box.rejected.connect(self._close)

    def _close(self):
        """Only option on dialog is a close button.

        Returns:
            True: Dialog has been closed.
        """
        self.done(True)


class SettingsDialog(QDialog):
    """Dialog that allows user to change application settings.
    """

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.setWindowIcon(
            QIcon(resource_filename('icons/clipmanager.ico')))
        self.setWindowTitle('Settings')
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setup_ui()

    def setup_ui(self):
        """Display each setting widget with saved values from registry/ini.

        Todo:
            Renable word_wrap widget when QDelegate Sizing issue fixed.
        """
        # Global hot key
        self.key_combo_edit = HotKeyEdit(self)
        self.key_combo_edit.setText(settings.get_global_hot_key())

        # Number of lines to display
        self.line_count_spin = QSpinBox(self)
        self.line_count_spin.setRange(1, 10)
        self.line_count_spin.setValue(settings.get_lines_to_display())

        # Where to open the dialog
        self.open_at_pos_combo = QComboBox(self)
        self.open_at_pos_combo.addItem('Mouse cursor', 0)
        self.open_at_pos_combo.addItem('Last position', 1)
        self.open_at_pos_combo.addItem('System tray', 2)

        # Word wrap display text
        self.word_wrap = QCheckBox('Word wrap')
        self.word_wrap.setCheckState(_check_state(settings.get_word_wrap()))

        global_form = QFormLayout()
        global_form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        global_form.addRow('Global shortcut:', self.key_combo_edit)
        global_form.addRow('Open window at:', self.open_at_pos_combo)
        # global_form.addRow('Maximum entries:', self.entries_edit)
        # global_form.addRow('Expire after:', self.expire_edit)
        global_form.addRow('Lines to display:', self.line_count_spin)
        ######################

        # Manage History
        self.paste_check = QCheckBox('Paste in active window after '
                                     'selection')
        self.paste_check.setCheckState(_check_state(settings.get_send_paste()))

        self.entries_edit = QLineEdit(self)
        self.entries_edit.setText(str(settings.get_max_entries_value()))
        self.entries_edit.setToolTip('Ignored if set to 0 days.')
        self.entries_edit.setFixedWidth(50)

        self.expire_edit = QSpinBox(self)
        self.expire_edit.setRange(0, 60)
        self.expire_edit.setSuffix(' days')
        self.expire_edit.setToolTip('Ignored if set to 0 days.')
        self.expire_edit.setValue(settings.get_expire_value())

        manage_form = QFormLayout()
        manage_form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        manage_form.addRow('Maximum entries:', self.entries_edit)
        manage_form.addRow('Expire after:', self.expire_edit)

        manage_box = QGroupBox('Manage history:')
        manage_box.setAlignment(Qt.AlignLeft)
        manage_box.setLayout(manage_form)
        ######################

        # Ignore Applications
        ignore_box = QGroupBox('Ignore the following applications:')
        self.exclude_list = QLineEdit(self)
        self.exclude_list.setPlaceholderText('KeePass.exe;binaryname')
        self.exclude_list.setText(settings.get_exclude())

        # Create seperate layout for ignore applications
        ignore_layout = QVBoxLayout()
        ignore_layout.addWidget(self.exclude_list)
        ignore_box.setLayout(ignore_layout)
        ######################

        # Save and Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Save |
                                      QDialogButtonBox.Cancel)
        ######################

        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(global_form)
        main_layout.addWidget(self.paste_check)
        main_layout.addWidget(manage_box)
        # main_layout.addWidget(self.word_wrap)
        main_layout.addWidget(ignore_box)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        # LINUX: I use Windows key to move windows with my wm
        self.setFocus(Qt.PopupFocusReason)

        # Connect
        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.cancel)

    def save(self):
        """Save and sync settings and return to main window.
        """
        settings.set_global_hot_key(self.key_combo_edit.text())
        settings.set_lines_to_display(self.line_count_spin.value())
        settings.set_word_wrap(self.word_wrap.isChecked())
        settings.set_send_paste(self.paste_check.isChecked())
        settings.set_exclude(self.exclude_list.text())
        settings.set_max_entries_value(self.entries_edit.text())
        settings.set_expire_value(self.expire_edit.value())

        # Get data integer from combo box string
        index = self.open_at_pos_combo.currentIndex()
        userdata = self.open_at_pos_combo.itemData(index)
        settings.set_open_window_at(userdata)

        settings.sync()
        self.done(True)

    def cancel(self):
        """Close dialog. Object is destroyed so no need to revert each widget's
        values.
        """
        self.done(False)


class HotKeyEdit(QLineEdit):
    """Capture key presses for setting global hot key.

    Source: https://github.com/rokups/paste2box
    License: GNU General Public License v3.0
    """
    special_key_whitelist = [
        Qt.Key_Print,
        Qt.Key_ScrollLock,
        Qt.Key_Pause,
    ]

    special_key_with_modifiers = [
        Qt.Key_Tab,
        Qt.Key_CapsLock,
        Qt.Key_Escape,
        Qt.Key_Backspace,
        Qt.Key_Insert,
        Qt.Key_Delete,
        Qt.Key_Home,
        Qt.Key_End,
        Qt.Key_PageUp,
        Qt.Key_PageDown,
        Qt.Key_NumLock,
        Qt.UpArrow,
        Qt.RightArrow,
        Qt.DownArrow,
        Qt.LeftArrow,
    ]

    def __init__(self, *args, **kwargs):
        QLineEdit.__init__(self, *args, **kwargs)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setToolTip('Press ESC to clear.')

    def keyPressEvent(self, event):
        """Capture key and modifer presses and insert them as plain text.

        Example, user presses CTRL+ALT+H, then QLineEdit will display
        <CTRL><ALT>H.

        Args:
            event: QKeyEvent

        Returns:
            QLineEdit.keyPressEvent's to be processed.

        References:
            http://stackoverflow.com/questions/6647970/how-can-i-capture-qkey_sequence-from-qkeyevent-depending-on-current-keyboard-layo

        Todo:
            Code can be improved and be more user friendly.
        """
        key = event.key()

        key_sequence = 0
        mod = event.modifiers()

        if mod & Qt.MetaModifier:
            key_sequence |= int(Qt.META)
        if mod & Qt.ShiftModifier:
            key_sequence |= int(Qt.SHIFT)
        if mod & Qt.ControlModifier:
            key_sequence |= int(Qt.CTRL)
        if mod & Qt.AltModifier:
            key_sequence |= int(Qt.ALT)

        if key in self.special_key_with_modifiers and not mod:
            if event.key() == Qt.Key_Escape:
                self.clear()

            return

        # Empty means a special key like F5, Delete, etc
        if event.text() == '' and key not in self.special_key_whitelist:
            return

        key_sequence |= int(key)

        self.setText(QKeySequence(key_sequence).toString(
            QKeySequence.NativeText))


class ConvertUpperCase(QValidator):
    """Convert text to upper case.
    """

    def __init__(self, parent=None):
        super(ConvertUpperCase, self).__init__(parent)

    def validate(self, text, pos):
        """Change input text to upper case.

        Args:
            text (unicode): Character or unicode.
            pos (int): Character position in QLineEdit.

        Returns:
            tuple (QValidator.State, str, int)
        """
        text = text.upper()
        return (QValidator.Intermediate, text, pos)


class AboutDialog(QDialog):
    """About dialog that displays information about application.
    """

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.parent = parent

        self.setWindowIcon(QIcon(resource_filename('icons/clipmanager.ico')))
        self.setWindowTitle('About')
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setup_ui()

    def setup_ui(self):
        """Display application name, version, company, and url.
        """
        app_name = QCoreApplication.applicationName()
        app_version = QCoreApplication.applicationVersion()
        app_domain = QCoreApplication.organizationDomain()

        # Application logo
        # app_pixmap = QPixmap('icons/app.ico')
        # scale_size = QSize(50, 50)
        # app_pixmap = app_pixmap.scaled(scale_size, Qt.IgnoreAspectRatio,
        #                                Qt.FastTransformation)
        # app_logo = QLabel()
        # app_logo.setFixedSize(scale_size)
        # app_logo.setPixmap(app_pixmap)
        # app_logo.setAlignment(Qt.AlignHCenter)

        # Company url
        app_url = QLabel('<a href="%s">%s</a>' % (app_domain, app_domain))
        app_url.setTextFormat(Qt.RichText)
        app_url.setTextInteractionFlags(Qt.TextBrowserInteraction)
        app_url.setOpenExternalLinks(True)

        # Close button
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
        """Only option on dialog is to close.

        Returns:
            True
        """
        self.done(True)
