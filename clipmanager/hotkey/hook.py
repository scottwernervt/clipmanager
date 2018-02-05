"""
Source: https://github.com/rokups/paste2box
License: GNU General Public License v3.0
"""

import struct
from ctypes import byref, c_char_p, c_size_t, c_void_p, cast, windll
from ctypes.wintypes import DWORD

PAGE_EXECUTE_READWRITE = 0x40


def hotpatch(source, destination):
    source = cast(source, c_void_p).value
    destination = cast(destination, c_void_p).value
    old = DWORD()
    if windll.kernel32.VirtualProtect(source - 5, 8, PAGE_EXECUTE_READWRITE,
                                      byref(old)):
        try:
            written = c_size_t()
            jmp_code = struct.pack('<BI', 0xE9,
                                   (destination - source) & 0xFFFFFFFF)
            windll.kernel32.WriteProcessMemory(-1, source - 5,
                                               cast(jmp_code, c_char_p),
                                               len(jmp_code), byref(written))
            windll.kernel32.WriteProcessMemory(-1, source,
                                               cast(struct.pack('<H', 0xF9EB),
                                                    c_char_p), 2,
                                               byref(written))
        finally:
            windll.kernel32.VirtualProtect(source - 5, 8, old, byref(old))
    return source + 2


def unhotpatch(source):
    source = cast(source, c_void_p).value
    old = DWORD()
    if windll.kernel32.VirtualProtect(source, 2, PAGE_EXECUTE_READWRITE,
                                      byref(old)):
        try:
            written = c_size_t()
            windll.kernel32.WriteProcessMemory(-1, source,
                                               cast(b'\x8B\xFF', c_char_p), 2,
                                               byref(written))
        finally:
            windll.kernel32.VirtualProtect(source, 2, old, byref(old))
