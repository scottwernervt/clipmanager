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


def format_title(title):
    """Format clipboard text for display in history view list.

    :param title: Title to format.
    :type title: str

    :return: Formatted text.
    :rtype: str
    """
    modified = textwrap.dedent(title)
    return modified.replace('\t', '    ')


def truncate_lines(text, count):
    """Truncate string based on line count.

    Counts number of line breaks in text and removes extra lines
    based on line_count value. If lines are removed, appends '...'
    to end of text to inform user of truncation.

    :param text: Single or multi-line string.
    :type text: str

    :param count: Number of lines to return.
    :type count: int

    :return: Truncated text string.
    :rtype: str
    """
    lines = [line for line in text.splitlines() if line.strip()]
    text = '\n'.join(lines[:count])
    if len(lines) > count:
        text += '...'
    return text


def resource_filename(file_name):
    """Load resource from resource package.

    :param file_name: File name of resource, e.g. icons\app.ico.
    :type file_name: str

    :return: Absolute path to resource file found locally on disk OR a true
        filesystem path for specified resource.
    :rtype:
    """
    paths = map(
        lambda p: os.path.join(p, file_name),
        (
            os.path.dirname(sys.argv[0]),  # Win: Executing path of exe
        ),
    )
    for path in paths:
        if os.path.isfile(path):
            logger.debug(path)
            return path

    return pkg_resources.resource_filename('clipmanager', file_name)
