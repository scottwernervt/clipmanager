from PySide.QtCore import Qt
from PySide.QtGui import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QIcon,
    QKeySequence,
    QLineEdit,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
)

from clipmanager.settings import settings
from clipmanager.ui.icons import get_icon


def _qcheckbox_state(state):
    """Toggle QCheckBox based on boolean state.

    :param state: Enabled or disabled.
    :type state: bool

    :return: Checked or unchecked.
    :rtype: Qt.Checked/Qt.Unchecked
    """
    return Qt.Checked if state else Qt.Unchecked


class SettingsDialog(QDialog):
    """Settings dialog for changing application preferences."""

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.setWindowIcon(get_icon('clipmanager.ico'))
        self.setWindowTitle('Settings')
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setup_ui()

    def setup_ui(self):
        """Setup Settings Dialog UI.

        TODO: Re-enable word_wrap widget when QDelegate Sizing issue fixed.

        :return: None
        :rtype: None
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
        self.word_wrap.setCheckState(_qcheckbox_state(settings.get_word_wrap()))

        global_form = QFormLayout()
        global_form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        global_form.addRow('Global shortcut:', self.key_combo_edit)
        global_form.addRow('Open window at:', self.open_at_pos_combo)
        # global_form.addRow('Maximum entries:', self.entries_edit)
        # global_form.addRow('Expire after:', self.expire_edit)
        global_form.addRow('Lines to display:', self.line_count_spin)

        # Manage History
        self.paste_check = QCheckBox('Paste in active window after '
                                     'selection')
        self.paste_check.setCheckState(
            _qcheckbox_state(settings.get_send_paste()))

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

        # Ignore Applications
        ignore_box = QGroupBox('Ignore the following applications:')
        self.exclude_list = QLineEdit(self)
        self.exclude_list.setPlaceholderText('KeePass.exe;binaryname')
        self.exclude_list.setText(settings.get_exclude())

        # Create separate layout for ignore applications
        ignore_layout = QVBoxLayout()
        ignore_layout.addWidget(self.exclude_list)
        ignore_box.setLayout(ignore_layout)
        # Save and Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Save |
                                      QDialogButtonBox.Cancel)

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

        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.cancel)

    def save(self):
        """Save settings and and close the dialog.

        :return: None
        :rtype: None
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
        """Do not save settings and close the dialog.

        :return: None
        :rtype: None
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
        self.setToolTip('Press ESC to clear_text.')

    def keyPressEvent(self, event):
        """Capture key and modifier presses and insert then.

        References:
        http://stackoverflow.com/questions/6647970/how-can-i-capture-qkey_sequence-from-qkeyevent-depending-on-current-keyboard-layo

        :param event:
        :type event: QKeyEvent

        :return:
        :rtype:  QLineEdit.keyPressEvent
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
