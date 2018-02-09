import logging
import os
import sys
import textwrap
import zlib

import pkg_resources
from PySide.QtCore import QTextCodec, QTextEncoder

logger = logging.getLogger(__name__)


def create_full_title(mime_data):
    """Create full title from mime data.

    Extract a title from QMimeData using urls, html, or text.

    :param mime_data:
    :type mime_data: QMimeData

    :return: Full title or None if it did not have any text/html/url.
    :rtype: str or None
    """
    if mime_data.hasUrls():
        urls = [url.toString() for url in mime_data.urls()]
        return 'Copied File(s):\n' + '\n'.join(urls)
    elif mime_data.hasText():
        return mime_data.text()
    elif mime_data.hasHtml():  # last resort
        return mime_data.html()
    else:
        logger.warning(
            'Failed to create a title from the following formats: %s',
            ','.join(mime_data.formats()))
        return '<unknown>'


def calculate_checksum(mime_data):
    """Calculate CRC checksum based on urls, html, or text.

    :param mime_data: Data from clipboard.
    :type mime_data: QMimeData

    :return: CRC32 checksum.
    :rtype: int
    """
    # if mime_data.hasImage():
    #     image = mime_data.imageData()
    #     ba = QByteArray()
    #     buff = QBuffer(ba)
    #     image.save(buff, 'PNG')
    #     byte_array = QByteArray(buff.buffer())
    #     buff.close()
    #     checksum_string = str(byte_array.toBase64())
    if mime_data.hasUrls():
        checksum_str = str(mime_data.urls())
    elif mime_data.hasHtml():
        checksum_str = mime_data.html()
    elif mime_data.hasText():
        checksum_str = mime_data.text()
    else:
        logger.warn('Mime Data does not have text, html, or urls.')
        return None

    # encode unicode characters for crc library
    codec = QTextCodec.codecForName('UTF-8')
    encoder = QTextEncoder(codec)
    byte_array = encoder.fromUnicode(checksum_str)  # QByteArray

    checksum = zlib.crc32(byte_array)
    return checksum


def format_title(text):
    """Dedent text and replace tab's with spaces.

    Args:
        text (unicode): Single or multi-line text with or without indentation.

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
        logger.exception(err)
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
        lambda p: os.path.join(p, file_name),
        (
            os.path.dirname(sys.argv[0]),  # Win: Executing path of exe
            # Add possible linux paths
        ),
    )
    # Return physical path to file if exists
    for path in paths:
        if os.path.isfile(path):
            logger.debug(path)
            return path

    # Return to resource path
    logger.debug('Using resource filename.')
    return pkg_resources.resource_filename('clipmanager', file_name)
