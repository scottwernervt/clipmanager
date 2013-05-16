#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from PySide import QtCore
from PySide import QtGui
from PySide import QtWebKit

from settings import settings
from utils import resource_filename

logging.getLogger(__name__)


def _check_state(state):
    """Toggle QtGui.QCheckBox based on boolean state.

    Args:
        state (int/boolean): Checked or not checked.

    Returns:
        QtCore.Qt.Checked/QtCore.Qt.Unchecked
    """
    if state:
        return QtCore.Qt.Checked
    else:
        return QtCore.Qt.Unchecked


class PreviewDialog(QtGui.QDialog):
    """Dialog to display model full contents.
    
    Todo:
        Allow user to edit data and save it back to database.
    """
    def __init__(self, parent=None):
        super(PreviewDialog, self).__init__(parent)
        self.parent = parent
        
        self.setWindowIcon(QtGui.QIcon(resource_filename('icons/app.ico')))
        self.setWindowTitle('Preview')
        self.resize(QtCore.QSize(500,300))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def setup_ui(self, mime_data):
        """Determine what to display based on mime data formats.

        If mime_data has html, then use QWebView to display content: tables,
        images, etc. If mime_data has plain text, then use QTextEdit to display 
        contents.

        Args:
            mime_data: QtCore.QMimeData
        """
        # if mime_data.hasImage():
        #     pass
        #     image = QtGui.QImage(mime_data.imageData())
        #     # print type(image)
        #     doc = QtGui.QLabel()
        #     pixmap = QtGui.QPixmap.fromImage(image)
        #     doc.setPixmap(pixmap)

        # Allow images to be loaded if html
        if mime_data.hasHtml():
            doc = QtWebKit.QWebView(self)
            doc.settings().setAttribute(
                QtWebKit.QWebSettings.LocalContentCanAccessRemoteUrls, True)
            doc.settings().setAttribute(
                QtWebKit.QWebSettings.LocalContentCanAccessFileUrls, True)
            doc.setHtml(mime_data.html())
        else:
            doc = QtGui.QTextEdit(self)

            if mime_data.hasUrls():
                text = 'Copied File(s): '
                for url in mime_data.urls():
                    text += url.toLocalFile() + '\n'
                doc.setPlainText(text)

            elif doc.canInsertFromMimeData(mime_data):
                doc.insertFromMimeData(mime_data)

            else:
                doc.setPlainText(('Unknown error has occured.\n'
                                  'Formats: %s' % mime_data.formats()))

            # Move cursor to top causing scrollbar to move to top
            doc.moveCursor(QtGui.QTextCursor.Start)
            doc.ensureCursorVisible()
            doc.setReadOnly(True)   # Do not support editing data yet

        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close)
        button_box.setFocus()
        
        layout = QtGui.QGridLayout(self)
        layout.addWidget(doc, 0, 0)
        layout.addWidget(button_box, 1, 0)
        self.setLayout(layout)

        button_box.rejected.connect(self._close)

    def _close(self):
        """Only option on dialog is a close button.

        Returns:
            True: Dialog has been closed.
        """
        self.done(True)


class SettingsDialog(QtGui.QDialog):
    """Dialog that allows user to change application settings.
    """
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.parent = parent

        self.setWindowIcon(QtGui.QIcon(resource_filename('icons/app.ico')))
        self.setWindowTitle('Settings')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setup_ui()

    def setup_ui(self):
        """Display each setting widget with saved values from registry/ini.

        Todo:
            Renable word_wrap widget when QDelegate Sizing issue fixed.
        """
        self.key_combo_edit = HotKeyEdit(self)

        # Allow user to insert <SUPER> on a Win OS
        self.super_check = QtGui.QCheckBox('Win')
        self.super_check.setToolTip('Insert <SUPER>')
        if '<SUPER>' in self.key_combo_edit.text().upper():
            self.super_check.setCheckState(QtCore.Qt.Checked)

        # Number of lines to display
        self.line_count_spin = QtGui.QSpinBox(self)
        self.line_count_spin.setRange(1, 10)
        self.line_count_spin.setValue(settings.get_lines_to_display())

        # Where to open the dialog
        self.open_at_pos_combo = QtGui.QComboBox(self)
        self.open_at_pos_combo.addItem('Mouse cursor', 0)
        self.open_at_pos_combo.addItem('Last position', 1)
        self.open_at_pos_combo.addItem('System tray', 2)

        # Word wrap display text
        self.word_wrap = QtGui.QCheckBox('Word wrap')
        self.word_wrap.setCheckState(_check_state(settings.get_word_wrap()))

        # Send paste key stroke when content set to clipboard
        self.paste_check = QtGui.QCheckBox('Paste in active window after '
                                           'selection')
        self.paste_check.setCheckState(_check_state(settings.get_send_paste()))

        # Ignore applications
        group_box = QtGui.QGroupBox('Ignore the following applications')
        self.exclude_list = QtGui.QLineEdit(self)
        self.exclude_list.setPlaceholderText('KeePass.exe;binaryname')
        self.exclude_list.setText(settings.get_exclude())

        # Create seperate layout for ignore applications
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.exclude_list)
        group_box.setLayout(vbox)

        # Save and cancel buttons
        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Save|
                                            QtGui.QDialogButtonBox.Cancel)

        # Create form layout to align widgets
        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        layout.addRow('Global shortcut:', self.key_combo_edit)
        layout.addRow('', self.super_check)
        layout.addRow('Open window at:', self.open_at_pos_combo)
        layout.addRow('Lines to display:', self.line_count_spin)

        # Set main layout
        main_layout = QtGui.QVBoxLayout(self)
        main_layout.addLayout(layout)
        # main_layout.addWidget(self.word_wrap)
        main_layout.addWidget(self.paste_check)
        main_layout.addWidget(group_box)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        # LINUX: I use Windows key to move windows with my wm
        self.setFocus(QtCore.Qt.PopupFocusReason)

        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.cancel)

        self.connect(self.super_check, QtCore.SIGNAL('stateChanged(int)'), 
                     self.insert_win_key)

    def insert_win_key(self):
        """Insert <SUPER> into key combo box for Windows machines.

        Windows captures <SUPER> key being pressed so we cannot capture it.
        """
        if self.super_check.isChecked():
            self.key_combo_edit.clear()
            self.key_combo_edit.setText('<Super>')
        else:
            self.key_combo_edit.setText(settings.get_global_hot_key())

    def save(self):
        """Save and sync settings and return to main window.
        """
        settings.set_global_hot_key(self.key_combo_edit.text())
        settings.set_lines_to_display(self.line_count_spin.value())
        settings.set_word_wrap(self.word_wrap.isChecked())
        settings.set_send_paste(self.paste_check.isChecked())
        settings.set_exclude(self.exclude_list.text())

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


class HotKeyEdit(QtGui.QLineEdit):
    """Capture key presses for setting global hot key.
    """
    def __init__(self, parent=None):
        super(HotKeyEdit, self).__init__(parent)
        self.parent = parent

        self.setValidator(ConvertUpperCase(self))
        self.setText(settings.get_global_hot_key())
        # self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setToolTip('Press one key at a time.\nPress ESCAPE to clear.')
        self.setFixedWidth(130)

    def keyPressEvent(self, event):
        """Capture key and modifer presses and insert them as plain text.

        Example, user presses CTRL+ALT+H, then QLineEdit will display
        <CTRL><ALT>H.

        Args:
            event: QtGui.QKeyEvent

        Returns:
            QLineEdit.keyPressEvent's to be processed.

        References:
            http://stackoverflow.com/questions/6647970/how-can-i-capture-qkey_sequence-from-qkeyevent-depending-on-current-keyboard-layo

        Todo:
            Code can be improved and be more user friendly.
        """
        # ESCAPE key pressed so clear text
        if event.key() == QtCore.Qt.Key_Escape:
            self.clear()

            if self.parent.super_check.isChecked():
                self.setText('<Super>')

            return False

        # Get current text to append to
        mod_seq = self.text()

        # Insert modifier text if pressed
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            mod_seq += '<Shift>'
        if event.modifiers() == QtCore.Qt.ControlModifier:
            mod_seq += '<Ctrl>'
        if event.modifiers() == QtCore.Qt.AltModifier:
            mod_seq += '<Alt>'
        if event.modifiers() == QtCore.Qt.MetaModifier:
            mod_seq += '<Super>'
        
        # Set new text based on key press
        self.setText(mod_seq)

        # Allow other events to process
        return QtGui.QLineEdit.keyPressEvent(self, event)


class ConvertUpperCase(QtGui.QValidator):
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
            tuple (QtGui.QValidator.State, str, int)
        """
        text = text.upper()
        return (QtGui.QValidator.Intermediate, text, pos)


class AboutDialog(QtGui.QDialog):
    """About dialog that displays information about application.
    """
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.parent = parent

        self.setWindowIcon(QtGui.QIcon(resource_filename('icons/app.ico')))
        self.setWindowTitle('About')
        self.resize(QtCore.QSize(350,200))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setup_ui()

    def setup_ui(self):
        """Display application name, version, company, and url.
        """
        app_name = QtCore.QCoreApplication.applicationName()
        app_version = QtCore.QCoreApplication.applicationVersion()
        app_org = QtCore.QCoreApplication.organizationName()
        app_domain = QtCore.QCoreApplication.organizationDomain()

        # Application logo
        app_pixmap = QtGui.QPixmap('icons/app.ico')
        scale_size = QtCore.QSize(50, 50)
        app_pixmap = app_pixmap.scaled(scale_size, QtCore.Qt.IgnoreAspectRatio, 
                                       QtCore.Qt.FastTransformation)
        app_logo = QtGui.QLabel()
        app_logo.setFixedSize(scale_size)
        app_logo.setPixmap(app_pixmap)
        app_logo.setAlignment(QtCore.Qt.AlignHCenter)

        # Company url. Todo: Remove mailto when I have a domain/company name
        company_url = QtGui.QLabel('<a href="%s">%s</a>' % (app_domain, 
                                                            app_domain))
        company_url.setTextFormat(QtCore.Qt.RichText)
        company_url.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        company_url.setOpenExternalLinks(True)

        with open (resource_filename('license.txt'), 'r') as license_file:
            about_text = license_file.read()

        about_doc = QtGui.QTextEdit()
        about_doc.setReadOnly(True)
        about_doc.setPlainText(about_text)
        # about_doc.setHtml(about_text)

        # Close button
        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close)
 
        layout = QtGui.QGridLayout()
        # layout.addWidget(app_logo, 0, 0, 4, 1)

        layout.addWidget(QtGui.QLabel('Name:'), 0, 0)
        layout.addWidget(QtGui.QLabel(app_name), 0, 1)

        layout.addWidget(QtGui.QLabel('Version:'), 1, 0)
        layout.addWidget(QtGui.QLabel(app_version), 1, 1)

        layout.addWidget(QtGui.QLabel('Company:'), 2, 0)
        layout.addWidget(QtGui.QLabel(app_org), 2, 1)

        layout.addWidget(QtGui.QLabel('Url:'), 3, 0)
        layout.addWidget(company_url, 3, 1)

        layout.addWidget(about_doc, 4, 0, 1, 4)
        layout.addWidget(button_box, 5, 0, 1, 4)

        self.setLayout(layout)

        button_box.rejected.connect(self.close)

    def close(self):
        """Only option on dialog is to close.

        Returns:
            True
        """
        self.done(True)
