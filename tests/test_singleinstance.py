#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import sys
import time
from threading import Thread

sys.path.append('..')
from clipmanager import singleinstance


kill = False

def _fake_app():
	global kill

	instance = singleinstance.SingleInstance()
	while kill:
		time.sleep(1)


class TestSingleInstance(object):

	def test_is_running(self):
		global kill
		# Application is not running
		# assert (self.instance.is_running() == False)
		app = Thread(target=_fake_app, args=())
		app.start()

		# Creating a 2nd instance will say it is already running
		instance = singleinstance.SingleInstance()
		assert (instance.is_running() == True)

		# Exit thread
		kill = False

	def test_is_not_running(self):
		# Application is not running
		instance = singleinstance.SingleInstance()
		assert (instance.is_running() == False)
