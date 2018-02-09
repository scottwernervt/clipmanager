import logging

from PySide.QtCore import QObject, QPoint, QSettings, QSize

from clipmanager.defs import APP_NAME, APP_ORG

logger = logging.getLogger(__name__)


class Settings(QObject):
    """Allows other modules to access application settings.

    Todo:
        Possibly change to requesting settings by string instead of defining
        functions for each.
    """

    def __init__(self, parent=None):
        super(QObject, self).__init__(parent)

        self.q_settings = QSettings(APP_ORG, APP_NAME)

    def sync(self):
        """Sync settings to storage method.
        """
        self.q_settings.sync()

    def get_disconnect(self):
        """Get disconnect from clipboard setting.

        :return: True if enabled, False if disabled.
        :rtype: int
        """
        return int(self.q_settings.value('disconnect', 0))

    def set_disconnect(self, value):
        """Set disconnect setting value.

        :param value: True if disconnected or false if connected.
        :type value: bool

        :return: None
        :rtype: None
        """
        self.q_settings.setValue('disconnect', int(value))

    def get_exclude(self):
        """Get application exclusion string list.

        :return: String list separated by a semicolon, keepassxc;chromium.
        :rtype: str
        """
        return self.q_settings.value('exclude', str(''))

    def set_exclude(self, value):
        """Set application exclusion string list.

        :param value: String list separated by a semicolon, keepassxc;chromium.
        :type value: str

        :return: None
        :rtype: None
        """
        applications = [app.strip() for app in value.split(';') if app]
        exclude = ';'.join(applications)
        if len(exclude) != 0 and not exclude.endswith(';'):
            exclude += ';'
        self.q_settings.setValue('exclude', str(exclude))

    def get_global_hot_key(self):
        """Get global hoy key shortcut.

        :return: Defaults to Ctrl+Shift+H.
        :rtype: str
        """
        return str(self.q_settings.value('globalhotkey', 'Ctrl+Shift+H'))

    def set_global_hot_key(self, value):
        self.q_settings.setValue('globalhotkey', str(value))

    def get_lines_to_display(self):
        return int(self.q_settings.value('linestodisplay', 4))

    def set_lines_to_display(self, value):
        self.q_settings.setValue('linestodisplay', int(value))

    def get_open_window_at(self):
        return int(self.q_settings.value('openwindowat', 0))

    def set_open_window_at(self, value):
        self.q_settings.setValue('openwindowat', int(value))

    def get_send_paste(self):
        return int(self.q_settings.value('sendpaste', 1))

    def set_send_paste(self, value):
        self.q_settings.setValue('sendpaste', int(value))

    def set_window_pos(self, value):
        self.q_settings.setValue('windowpos', value)

    def get_window_pos(self):
        return self.q_settings.value('windowpos', QPoint(0, 0))

    def set_window_size(self, value):
        self.q_settings.setValue('windowsize', value)

    def get_window_size(self):
        return self.q_settings.value('windowsize', QSize(275, 230))

    def get_word_wrap(self):
        # return int(self.q_settings.value('wordwrap', 0))
        return False

    def set_word_wrap(self, value):
        self.q_settings.setValue('wordwrap', int(value))

    def get_max_entries_value(self):
        return int(self.q_settings.value('maxentriesvalue', 300))

    def set_max_entries_value(self, value):
        self.q_settings.setValue('maxentriesvalue', int(value))

    def get_expire_value(self):
        return int(self.q_settings.value('expirevalue', 14))

    def set_expire_value(self, value):
        self.q_settings.setValue('expirevalue', int(value))


settings = Settings()
