#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: Look into X11 lib http://pastebin.com/GMLjeAg1

# import os
import logging
logging.getLogger(__name__)
import subprocess


def send_event():
	"""Send paste key stroke to active window.

	Returns:
		True: xdotool executed with zero exit code.
		False: xdotool executed with non zero exit code. Most likely, the user
			does not have it installed.
	"""
	cmd = "/bin/sh -c 'xdotool key --delay 100 ctrl+v'"

	logging.info('Paste action sent.')
	logging.debug('cmd: %s' % cmd)

	process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)

	# Wait for the process to terminate
	out, err = process.communicate()
	errcode = process.returncode

	if errcode != 0:
		logging.warn('std.out: %s' % out)
		logging.warn('std.err: %s' % err)
		logging.warn('Exit code: %s' % errcode)

		return False
	else:
		return True