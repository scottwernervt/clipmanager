#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

# import keybinder
from PySide import QtCore

logging.getLogger(__name__)


class Binder(QtCore.QObject):

    def __init__(self, action=None, parent=None):
        super(Binder, self).__init__(parent)
        self.parent = parent

    def bind(self, key_seq, action):
        logging.info('Binding key seq %s to : %s' % (key_seq, action))

    # return keybinder.bind(key_seq, action)

    def unbind(self, key_seq):
        logging.info('Unbinding key seq: %s' % key_seq)
    # try:
    # 	keybinder.unbind(key_seq)
    # except KeyError as err:
    # 	# KeyError: 'bind: keystring is not bound'
    # 	logging.warn(err)
