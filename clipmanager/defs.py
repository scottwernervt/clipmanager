import os

# Formats to check and save with from OS clipboard
MIME_SUPPORTED = [
    'text/html',
    'text/html;charset=utf-8',
    'text/plain',
    'text/plain;charset=utf-8',
    'text/richtext',
    'application/x-qt-windows-mime;value="Rich Text Format"',
    'text/uri-list',
    # 'application/x-qt-image'
]

if os.name == 'posix':
    MIME_SUPPORTED.append('x-special/gnome-copied-files')
