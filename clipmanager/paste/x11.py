#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: Look into X11 lib http://pastebin.com/GMLjeAg1

# import os
import logging
import subprocess

logger = logging.getLogger(__name__)


def send_event():
    """Send paste key stroke to active window.

    Returns:
        True: xdotool executed with zero exit code.
        False: xdotool executed with non zero exit code. Most likely, the user
            does not have it installed.
    """
    cmd = "/bin/sh -c 'xdotool key --delay 100 ctrl+v'"

    logger.info('Paste action sent.')
    logger.debug('cmd: %s', cmd)

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    # Wait for the process to terminate
    out, err = process.communicate()
    errcode = process.returncode

    if errcode != 0:
        logger.warn('std.out: %s' % out)
        logger.warn('std.err: %s' % err)
        logger.warn('Exit code: %s' % errcode)

        return False
    else:
        return True
