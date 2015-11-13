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

import binascii


class Connection(object):
    _address = None
    _sock = None
    _buffer = None

    def __init__(self, server, address, sock):
        """
        Creates a connection object

        :param address: Address
        :type address tuple
        :param sock: Socket
        :type sock socket.socket
        """
        self._address = address
        self._sock = sock
        self.server = server

        self._sock.setblocking(0)

    def send(self, data):
        self._sock.send(data)

    def flush(self):
        success = False
        buf = b""

        while True:
            try:
                buf += self._sock.recv(1024)
                success = True
            except BlockingIOError:
                break

        if success:
            self.server.data_hook(self, buf)

    def get_address(self):
        return self._address