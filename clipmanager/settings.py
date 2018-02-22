from PySide.QtCore import QObject, QPoint, QSettings, QSize


class Settings(QObject):
    """Allows other modules to access application settings.

    Todo:
        Possibly change to requesting settings by string instead of defining
        functions for each.
    """

    def __init__(self, parent=None):
        super(QObject, self).__init__(parent)

        self.q_settings = QSettings()

    def filename(self):
        """Wrapper around QSettings.filename()

        :return: Path to app's setting ini file.
        :rtype: str
        """
        return self.q_settings.fileName()

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
        return self.q_settings.value('exclude_app', str(''))

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
        self.q_settings.setValue('exclude_app', str(exclude))

    def get_global_hot_key(self):
        """Get global hoy key shortcut.

        :return: Defaults to Ctrl+Shift+H.
        :rtype: str
        """
        return str(self.q_settings.value('global_hot_key', 'Ctrl+Shift+H'))

    def set_global_hot_key(self, value):
        self.q_settings.setValue('global_hot_key', str(value))

    def get_lines_to_display(self):
        return int(self.q_settings.value('line_count', 4))

    def set_lines_to_display(self, value):
        self.q_settings.setValue('line_count', int(value))

    def get_open_window_at(self):
        return int(self.q_settings.value('open_at', 0))

    def set_open_window_at(self, value):
        self.q_settings.setValue('open_at', int(value))

    def get_send_paste(self):
        return int(self.q_settings.value('send_paste', 1))

    def set_send_paste(self, value):
        self.q_settings.setValue('send_paste', int(value))

    def set_window_pos(self, value):
        self.q_settings.setValue('window_position', value)

    def get_window_pos(self):
        return self.q_settings.value('window_position', QPoint(0, 0))

    def set_window_size(self, value):
        self.q_settings.setValue('window_size', value)

    def get_window_size(self):
        return self.q_settings.value('window_size', QSize(275, 230))

    def get_max_entries_value(self):
        return int(self.q_settings.value('max_entries', 300))

    def set_max_entries_value(self, value):
        self.q_settings.setValue('max_entries', int(value))

    def get_expire_value(self):
        return int(self.q_settings.value('expire_at', 14))

    def set_expire_value(self, value):
        self.q_settings.setValue('expire_at', int(value))

    def clear(self):
        self.q_settings.clear()
