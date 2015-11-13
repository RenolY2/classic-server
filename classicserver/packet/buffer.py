"""
    classic-server - A basic Minecraft Classic server.
    Copyright (C) 2015  SopaXorzTaker

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class ReadOnlyError(IOError):
    pass

class WriteOnlyError(IOError):
    pass


class Buffer(object):
    _buf = None
    _offset = None

    def __init__(self, buf=None, offset=None):
        self._buf = buf if buf else b""
        self._offset = offset if offset else 0

    def read(self, length, modify_offset=True):
        if (self._offset+length) <= len(self._buf):
            val = self._buf[self._offset:self._offset+length]
            if modify_offset:
                self._offset += length
            return val
        else:
            raise IndexError("Buffer is too small")

    def write(self, data):
        self._offset = len(self._buf)
        self._buf += data
        self._offset += len(data)

    def get_buffer(self):
        return self._buf

    def left(self):
        return (len(self._buf) - self._offset)


class ReadBuffer(Buffer):
    def write(self, data):
        raise ReadOnlyError("The buffer is read-only")


class WriteBuffer(Buffer):
    def read(self, length, modify_offset=True):
        raise WriteOnlyError("The buffer is write-only")
