#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import sys
import time
from threading import Thread

sys.path.append('..')
from clipmanager import singleinstance


class TestSingleInstance(object):

	def test_is_not_running(self):
		# Application is not running
		instance = singleinstance.SingleInstance()
		assert (instance.is_running() == False)
		del instance

	def test_is_running(self):
		app_a = singleinstance.SingleInstance()
		app_b = singleinstance.SingleInstance()
		
		assert (app_b.is_running() == True)
		del app_a, app_b