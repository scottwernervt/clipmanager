#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import textwrap

logging.getLogger(__name__)


def clean_up_text(text):
    """Dedent text and replace tab's with spaces.

    Args:
        text (unicode): single or multline text with or without indentation.

    Returns:
        unicode: formatted text
    """
    text = textwrap.dedent(text)
    text = text.replace('\t', '    ')
    return  text.rstrip().lstrip()


def remove_extra_lines(text, line_count):
    """Truncate string based on line count.

    Counts number of line breaks in text and removes extra lines
    based on line_count value. If lines are removed, appends '...'
    to end of text to inform user of truncation.

    Args:
        text (str): Text that 
        line_count (int): Number of lines to keep.

    Returns:
        text (str): Extra lines removed from variables text
    """
    try:
        # Remove empty line breaks as we want to capture text not white space
        text = os.linesep.join([s for s in text.splitlines() if s])
    except AttributeError as err:
        logging.exception(err)
        return text

    # Split text by line breaks
    lines = text.split('\n')

    # Remove extra lines
    if len(lines) > line_count:
        text = '\n'.join(lines[:line_count])
        return '%s...' % text
    else:
        return text


# def strip_extra_char(text, length):
#     if len(text) > length:
#         return text[:length] + '...'
#     else:
#         return text
