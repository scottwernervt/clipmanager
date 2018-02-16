import logging
import textwrap

logger = logging.getLogger(__name__)


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
