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