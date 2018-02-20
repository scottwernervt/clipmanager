from PySide.QtCore import Qt, Slot
from PySide.QtGui import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QKeySequence,
    QLineEdit,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
)

from clipmanager.settings import Settings
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

        self.settings = Settings()

        self.setWindowTitle('Settings')
        self.setWindowIcon(get_icon('clipmanager.ico'))
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.key_combo_edit = HotKeyEdit(self)
        self.key_combo_edit.setText(self.settings.get_global_hot_key())

        self.line_count_spin = QSpinBox(self)
        self.line_count_spin.setRange(1, 10)
        self.line_count_spin.setValue(self.settings.get_lines_to_display())

        self.open_at_pos_combo = QComboBox(self)
        self.open_at_pos_combo.addItem('Mouse cursor', 0)
        self.open_at_pos_combo.addItem('Last position', 1)
        self.open_at_pos_combo.addItem('System tray', 2)

        global_form = QFormLayout()
        global_form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        global_form.addRow('Global shortcut:', self.key_combo_edit)
        global_form.addRow('Open window at:', self.open_at_pos_combo)
        global_form.addRow('Lines to display:', self.line_count_spin)

        self.paste_check = QCheckBox('Paste in active window after selection')
        self.paste_check.setCheckState(
            _qcheckbox_state(self.settings.get_send_paste())
        )

        self.entries_edit = QLineEdit(self)
        self.entries_edit.setText(str(self.settings.get_max_entries_value()))
        self.entries_edit.setToolTip('Ignored if set to 0 days.')
        self.entries_edit.setFixedWidth(50)

        self.expire_edit = QSpinBox(self)
        self.expire_edit.setRange(0, 60)
        self.expire_edit.setSuffix(' days')
        self.expire_edit.setToolTip('Ignored if set to 0 days.')
        self.expire_edit.setValue(self.settings.get_expire_value())

        manage_form = QFormLayout()
        manage_form.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        manage_form.addRow('Maximum entries:', self.entries_edit)
        manage_form.addRow('Expire after:', self.expire_edit)

        manage_box = QGroupBox('Manage history:')
        manage_box.setAlignment(Qt.AlignLeft)
        manage_box.setLayout(manage_form)

        ignore_box = QGroupBox('Ignore the following applications:')
        self.exclude_edit = QLineEdit(self)
        self.exclude_edit.setPlaceholderText('BinaryName;WindowTitle;')
        self.exclude_edit.setText(self.settings.get_exclude())

        ignore_layout = QVBoxLayout()
        ignore_layout.addWidget(self.exclude_edit)
        ignore_box.setLayout(ignore_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(global_form)
        main_layout.addWidget(self.paste_check)
        main_layout.addWidget(manage_box)
        main_layout.addWidget(ignore_box)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

        # X11: Give focus for window managers, e.g. i3.
        self.setFocus(Qt.PopupFocusReason)

        self.button_box.accepted.connect(self.save)
        self.button_box.rejected.connect(self.cancel)

    @Slot()
    def save(self):
        """Save settings and and close the dialog.

        :return: None
        :rtype: None
        """
        self.settings.set_global_hot_key(self.key_combo_edit.text())
        self.settings.set_lines_to_display(self.line_count_spin.value())
        self.settings.set_send_paste(self.paste_check.isChecked())
        self.settings.set_exclude(self.exclude_edit.text())
        self.settings.set_max_entries_value(self.entries_edit.text())
        self.settings.set_expire_value(self.expire_edit.value())

        open_at_index = self.open_at_pos_combo.currentIndex()
        open_at_value = self.open_at_pos_combo.itemData(open_at_index)
        self.settings.set_open_window_at(open_at_value)

        self.settings.sync()
        self.done(True)

    @Slot()
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

        self.setText(
            QKeySequence(key_sequence).toString(QKeySequence.NativeText)
        )
