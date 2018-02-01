#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import textwrap
import zlib

import pkg_resources
from PySide import QtCore

logging.getLogger(__name__)


def create_full_title(mime_data):
    """Create a title from QMimeData.

    Extract a title from QMimeData using hasUrls(), hasText(), or hasHtml().

    Args:
        mime_data: QMimeData

    Returns:
        str: title
        None: QMimeData did not have plain text, html, or url(s). 
    """
    # Plain text for title or covert to string for copied files
    text = None
    if mime_data.hasUrls():
        text = 'Copied File(s): '
        seperator = '\n'
        # if settings.get_word_wrap():
        #     seperator = ', '
        # else:
        #     seperator = '\n'
        for url in mime_data.urls():
            # '' means url is a web address so we don't want Copied File(s)
            if url.toLocalFile() == '':
                text = None
                break

            text += url.toString() + seperator

    # Set plain text
    if mime_data.hasText() and text == None:
        text = mime_data.text()

    # Last resort to create title
    if mime_data.hasHtml() and text == None:
        text = mime_data.html()

    logging.debug(text)
    return text


def calculate_checksum(mime_data):
    """Calculates checksum from mime_data contents.

    Calculate CRC32 checksum using byte data from clipboard contents. 

    Args:
        mime_data (QMimeData): data from clipboard

    Returns:
        None: Clipboard contents do not have text, html, or url. In other words,
              the format is not supported.
        checksum: QMimeData bytes converted to crc32.
    """
    checksum_str = None

    if mime_data.hasText():
        checksum_str = mime_data.text()
    if mime_data.hasHtml():
        checksum_str = mime_data.html()
    if mime_data.hasUrls():
        checksum_str = str(mime_data.urls())
    # if mime_data.hasImage():
    #     image = mime_data.imageData()
    #     ba = QtCore.QByteArray()
    #     buff = QtCore.QBuffer(ba)
    #     image.save(buff, 'PNG')
    #     byte_array = QtCore.QByteArray(buff.buffer())
    #     buff.close()
    #     checksum_string = str(byte_array.toBase64())

    # Ignore content that does not have text, html, or image
    if not checksum_str:
        logging.warn('Mime Data does not have text, html, or urls.')
        return None
    else:
        logging.debug('checksum_str=%s' % checksum_str)

    # CRASH FIX: Handle unicode characters for calculating checksum
    codec = QtCore.QTextCodec.codecForName('UTF-8')
    encoder = QtCore.QTextEncoder(codec)
    bytes = encoder.fromUnicode(checksum_str)  # QByteArray

    # Calculate checksum with crc32 method (quick)
    checksum = zlib.crc32(bytes)
    logging.debug('checksum=%s' % checksum)

    return checksum


def clean_up_text(text):
    """Dedent text and replace tab's with spaces.

    Args:
        text (unicode): Single or multline text with or without indentation.

    Returns:
        unicode: Input text dedented and tab's replaced by spaces.
    """
    modified = textwrap.dedent(text)
    return modified.replace('\t', '    ')


def remove_extra_lines(text, line_count):
    """Truncate string based on line count.

    Counts number of line breaks in text and removes extra lines
    based on line_count value. If lines are removed, appends '...'
    to end of text to inform user of truncation.

    Args:
        text (str): Single or multline line string.
        line_count (int): Number of lines to return.

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
    lines = text.splitlines()

    # Remove extra lines
    if len(lines) > line_count:
        text = '\n'.join(lines[:line_count])
        return '%s...' % text
    else:
        return text


def resource_filename(file_name):
    """Get data file on physical disk or from resource package.

    Args:
        file_name (str): names.dat, icons\app.ico

    Returns:
        path: Absolute path to resource file found locally on disk.
        pkg_resource: Return a true filesystem path for specified resource.
    """
    paths = map(
        lambda path: os.path.join(path, file_name),
        (
            os.path.dirname(sys.argv[0]),  # Win: Executing path of exe
            # Add possible linux paths
        ),
    )
    # Return physical path to file if exists
    for path in paths:
        if os.path.isfile(path):
            logging.debug(path)
            return path

    # Return to resource path
    logging.debug('Using resouce filename.')
    return pkg_resources.resource_filename('clipmanager', file_name)
