#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sys
sys.path.append('..')

from clipmanager import utils


# def test_clean_up_text():
# 	assert utils.clean_up_text(' strip spaces ') == 'strip spaces'
# 	assert utils.clean_up_text('\ttab1') == 'tab1'
# 	assert utils.clean_up_text('\tline1\n\t\tline2') == 'line1\n    line2'
# 	assert utils.clean_up_text('    4 spaces') == '4 spaces'

def test_remove_extra_lines():
	assert utils.remove_extra_lines('Line1', 1) == 'Line1'
	assert utils.remove_extra_lines('Line1\nLine2', 1) == 'Line1\r...'
	assert utils.remove_extra_lines('Line1\rLine2', 1) == 'Line1\r...'
	