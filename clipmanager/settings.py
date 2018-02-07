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
        """Disconnect from clipboard, yes or no?

        Returns:
            int: 1/0
                 Default value of 0
        """
        return int(self.q_settings.value('disconnect', 0))

    def set_disconnect(self, value):
        """Save disconnect from clipboard value. Convert boolean to integer.

        Args:
            value: True/False
        """
        logger.debug(value)
        self.q_settings.setValue('disconnect', int(value))

    def get_exclude(self):
        """Application exclude list.

        Returns:
            str: String list seperated by a semicolon, KeePass.exe;chromium
                 Default value is empty string.
        """
        return self.q_settings.value('exclude', str(''))

    def set_exclude(self, value):
        """Save application exclude string list.

        Clean up user input by eliminating spaces between ; and if they used
        a comma as a seperator then replace it with semicolons.

        Args:
            value (str): String list seperated by a semicolon, 
                         KeePass.exe;chromium
        """
        logger.debug(value)

        if value != '':
            # Handle user mistake in spacing
            data = value.replace('; ', ';')
            data = data.replace(' ;', ';')
            data = data.replace(',', ';')

            # Add ; at end
            if data[-1] != ';':
                data += ';'
        else:
            data = value

        self.q_settings.setValue('exclude', str(data))

    def get_global_hot_key(self):
        """Global hot key shortcut.

        Returns:
            str: Global hot key combination.
                 Default value is '<CTRL><ALT>H'
        """
        return str(self.q_settings.value('globalhotkey', 'Ctrl+Shift+H'))

    def set_global_hot_key(self, value):
        logger.debug(value)
        self.q_settings.setValue('globalhotkey', str(value))

    def get_lines_to_display(self):
        return int(self.q_settings.value('linestodisplay', 4))

    def set_lines_to_display(self, value):
        logger.debug(value)
        self.q_settings.setValue('linestodisplay', int(value))

    def get_open_window_at(self):
        return int(self.q_settings.value('openwindowat', 0))

    def set_open_window_at(self, value):
        logger.debug(value)
        self.q_settings.setValue('openwindowat', int(value))

    def get_send_paste(self):
        return int(self.q_settings.value('sendpaste', 1))

    def set_send_paste(self, value):
        logger.debug(value)
        self.q_settings.setValue('sendpaste', int(value))

    def set_window_pos(self, value):
        logger.debug(value)
        self.q_settings.setValue('windowpos', value)

    def get_window_pos(self):
        return self.q_settings.value('windowpos', QPoint(0, 0))

    def set_window_size(self, value):
        logger.debug(value)
        self.q_settings.setValue('windowsize', value)

    def get_window_size(self):
        return self.q_settings.value('windowsize', QSize(275, 230))

    def get_word_wrap(self):
        return False
        # return int(self.q_settings.value('wordwrap', 0))

    def set_word_wrap(self, value):
        logger.debug(value)
        self.q_settings.setValue('wordwrap', int(value))

    def get_max_entries_value(self):
        return int(self.q_settings.value('maxentriesvalue', 300))

    def set_max_entries_value(self, value):
        logger.debug(value)
        self.q_settings.setValue('maxentriesvalue', int(value))

    def get_expire_value(self):
        return int(self.q_settings.value('expirevalue', 14))

    def set_expire_value(self, value):
        logger.debug(value)
        self.q_settings.setValue('expirevalue', int(value))


settings = Settings()
