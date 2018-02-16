"""
Source: https://github.com/ActivityWatch/aw-watcher-x11/aw_watcher_x11/xprop.py
License: None
"""
import logging
import os
import re
import subprocess

logger = logging.getLogger(__name__)


def readlink_binary(pid):
    cmd = ['readlink', '-f', '/proc/%s/exe' % pid]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, close_fds=True)
    return p.stdout.read()


def xprop_id(window_id):
    cmd = ['xprop', '-id', window_id]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, close_fds=True)
    return p.stdout.read()


def xprop_root():
    cmd = ['xprop', '-root']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, close_fds=True)
    return p.stdout.read()


def get_active_window_id():
    lines = xprop_root().split('\n')
    client_list = next(
        iter(filter(lambda x: '_NET_ACTIVE_WINDOW(' in x, lines))
    )
    wid = re.findall("0x[0-9a-f]*", client_list)[0]
    return wid


def get_window_ids():
    lines = xprop_root().split('\n')
    client_list = next(iter(filter(lambda x: '_NET_CLIENT_LIST(' in x, lines)))
    window_ids = re.findall('0x[0-9a-f]*', client_list)
    return window_ids


def _extract_xprop_field(line):
    return ''.join(line.split('=')[1:]).strip(' \n')


def get_xprop_field(fieldname, xprop_output):
    return list(
        map(_extract_xprop_field, re.findall(fieldname + '.*\n', xprop_output)))


def get_xprop_field_str(fieldname, xprop_output):
    return get_xprop_field(fieldname, xprop_output)[0].strip('"')


def get_xprop_field_strlist(fieldname, xprop_output):
    return [s.strip('"') for s in get_xprop_field(fieldname, xprop_output)]


def get_xprop_field_class(xprop_output):
    return [c.strip('", ') for c in
            get_xprop_field('WM_CLASS', xprop_output)[0].split(',')]


def get_xprop_field_int(fieldname, xprop_output):
    return int(get_xprop_field(fieldname, xprop_output)[0])


def get_window(wid, active_window=False):
    s = xprop_id(wid)
    window = {
        'id': wid,
        'active': active_window,
        'name': get_xprop_field_str('WM_NAME', s),
        'class': get_xprop_field_class(s),
        'desktop': get_xprop_field_int('WM_DESKTOP', s),
        'command': get_xprop_field('WM_COMMAND', s),
        'role': get_xprop_field_strlist('WM_WINDOW_ROLE', s),
        'pid': get_xprop_field_int('WM_PID', s),
    }

    return window


def get_windows(wids, active_window_id=None):
    return [get_window(wid, active_window=(wid == active_window_id)) for wid in
            wids]


def get_x11_owner():
    owner_names = []

    wid = get_active_window_id()
    window = get_window(wid, True)

    window_classes = window.get('class', [])
    owner_names.extend(window_classes)

    window_name = window.get('name', '')
    if window_name:
        application_name = window_name.split('-')[-1].strip()
        owner_names.extend([window_name, application_name])

    binary_path = readlink_binary(window['pid'])
    binary_name = os.path.basename(binary_path.strip())
    if binary_name:
        owner_names.append(binary_name)

    return owner_names
